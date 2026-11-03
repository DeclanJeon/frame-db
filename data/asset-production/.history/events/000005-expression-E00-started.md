# Codex-native image route started

Date: 2026-10-30
Operation: expression-E00, attempt 3.
Status: started.
User decision: retain the requested Codex image route; do not substitute another generation service.
Diagnosis: the generic image extension selected the local OpenCode workbuddy API route and returned 404 for two model names. The installed Codex CLI instead reports its native `image_generation` feature enabled and has its own imagegen skill and subscription-auth path.
Method: invoke installed Codex with its built-in image tool for this one exact image. This is not the API-key CLI fallback script or another media service.
Prompt: `../prompts/expression-E00.md`.
Expected project destination: `public/generated/frame-assets/expression-E00.png`.
Do not claim success until a real output is returned and inspected.
