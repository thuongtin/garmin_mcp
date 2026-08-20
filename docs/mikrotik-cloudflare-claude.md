# Garmin MCP on MikroTik + Cloudflare + Claude.ai

Follow the shared playbook:

`/Users/ethan/github/oura-mcp/docs/remote-mcp-mikrotik-claude.md`

This instance:

| Piece | Value |
|---|---|
| Container | `garmin-mcp` |
| veth | `veth-garmin` `10.10.10.13/24` |
| Port | `8000` |
| Tokens | `GARMINTOKENS=/data` (`garmin_tokens.txt` on the router, copied to `garmin_tokens.json` at start) |
| Origin | `https://garmin.thuongtin.com` |
| Claude URL | `https://garmin-mcp-oauth.ho-31c.workers.dev/mcp` |
| PIN | `~/.garminconnect/oauth-approve-pin` |

HTTP off-loopback requires `GARMIN_MCP_HTTP_TOKEN`. `/healthz` and `/health` stay public.

```bash
docker build --platform linux/arm64 -t garmin-mcp:local .
docker save garmin-mcp:local -o garmin-mcp-arm64.tar
```

Claude.ai connector name: `Home Garmin MCP`. Leave OAuth Client ID empty.

## Lab status

- Container `garmin-mcp` on `veth-garmin` `10.10.10.13:8000`, tokens from `~/.garminconnect`.
- HTTP bearer required. PIN at `~/.garminconnect/oauth-approve-pin`.
- Worker: `https://garmin-mcp-oauth.ho-31c.workers.dev/mcp`.
- Origin: `https://garmin.thuongtin.com` on tunnel HomeMik (`http://10.10.10.13:8000`) with Access (email Allow + the same Service Token as Oura).
- Claude.ai: `https://garmin-mcp-oauth.ho-31c.workers.dev/mcp`
