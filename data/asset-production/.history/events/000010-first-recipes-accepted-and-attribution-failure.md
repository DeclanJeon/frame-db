# First representative assets accepted; output attribution tightened

Date: 2026-10-30
Accepted by parent direct full-image inspection: hair-E01, hair-E08, makeup-L03, gaze-left-level, makeup-N01, gesture-H07.
Together with expression-E00: 7 accepted unique images.

Hair-E08 is accepted for its visible frontal/lateral bob perimeter, fringe and identity only. The bob covers the nape; rear geometry is not verified. Hair-E01's actual cheek mole is on the subject-left side, so the initially arbitrary B marker-side specification was corrected before dependent production. Original submitted prompt remains preserved.

The makeup expansion launcher stopped after its first L01 native call because global newest-file discovery mixed another thread's unrelated image into the candidate list. No L01 output was copied or accepted, no repeat image call was made, and the other 31 jobs were not attempted. The failed receipt and exact submitted prompt remain on disk.

Execution contract now requires an exact current thread ID and restricts image-source discovery to that thread's directory. Future launchers retain Codex session history instead of ephemeral execution and expose `thread.started`/`FRAME_THREAD` to the parent. Never resolve this failure by selecting the globally newest file.

Integration also caught missing creative-parent IDs and overly strict identity-only reference validation. Parent added action-basis parents to 11 creative expression records, and explicit geometry/recipient roles to D11/H17 with primary identity retained. These are verified integration fixes, not new source facts.
