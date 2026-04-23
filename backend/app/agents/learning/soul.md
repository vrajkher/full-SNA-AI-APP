# Learning – Soul

## Behaviour
- JSON on disk is the single source of truth. In-memory state is never
  trusted across requests.
- Writes are serialised with a process-wide lock.
- Ships with sensible defaults (HSS / ADM / FIN / SAL prefixes) so the first
  run does something useful.

## Intelligence
- Accepts bulk corrections in one POST so the UI can batch a whole review
  session into a single write.
- Uses sorted, human-friendly JSON so the file can also be hand-edited.
