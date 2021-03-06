﻿using System;
using System.Linq;
using System.Threading.Tasks;
using CompatBot.Commands.Attributes;
using CompatBot.Utils;
using DSharpPlus.CommandsNext;
using DSharpPlus.CommandsNext.Attributes;
using DSharpPlus.Entities;

namespace CompatBot.Commands
{
    internal sealed partial class Moderation: BaseCommandModuleCustom
    {
        [Command("report"), RequiresWhitelistedRole]
        [Description("Adds specified message to the moderation queue")]
        public async Task Report(CommandContext ctx, [Description("Message ID from current channel to report")] ulong messageId, [RemainingText, Description("Optional report comment")] string comment = null)
        {
            try
            {
                var msg = await ctx.Channel.GetMessageAsync(messageId).ConfigureAwait(false);
                await ReportMessage(ctx, comment, msg);
            }
            catch (Exception)
            {
                await ctx.ReactWithAsync(Config.Reactions.Failure, "Failed to report the message").ConfigureAwait(false);
            }
        }

        [Command("report"), RequiresWhitelistedRole]
        [Description("Adds specified message to the moderation queue")]
        public async Task Report(CommandContext ctx, [Description("Message link to report")] string messageLink, [RemainingText, Description("Optional report comment")] string comment = null)
        {
            try
            {
                var msg = await ctx.GetMessageAsync(messageLink).ConfigureAwait(false);
                await ReportMessage(ctx, comment, msg);
            }
            catch (Exception)
            {
                await ctx.ReactWithAsync(Config.Reactions.Failure, "Failed to report the message").ConfigureAwait(false);
            }
        }

        private static async Task ReportMessage(CommandContext ctx, string comment, DiscordMessage msg)
        {
            if (msg.Reactions.Any(r => r.IsMe && r.Emoji == Config.Reactions.Moderated))
            {
                await ctx.ReactWithAsync(Config.Reactions.Failure, "Already reported").ConfigureAwait(false);
                return;
            }

            await ctx.Client.ReportAsync("Message report", msg, new[] {ctx.Message.Author}, comment, ReportSeverity.Medium).ConfigureAwait(false);
            await msg.ReactWithAsync(ctx.Client, Config.Reactions.Moderated).ConfigureAwait(false);
            await ctx.ReactWithAsync(Config.Reactions.Success, "Message reported").ConfigureAwait(false);
        }
    }
}
