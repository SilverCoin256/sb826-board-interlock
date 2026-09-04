export const meta = {
  name: 'extract-directors-llm',
  description: 'LLM-assisted director-name extraction over all fetched proxy-statement text windows',
  phases: [
    { title: 'List', detail: 'one agent lists all doc_ids from the windows file' },
    { title: 'Extract', detail: 'batches of document text windows, agents extract real director names only' },
  ],
}

const WINDOWS_PATH = '/Users/shaurya/CascadeProjects/sb826-board-interlock/data/director_windows_scaled.json'

const LIST_SCHEMA = {
  type: 'object',
  properties: {
    doc_ids: { type: 'array', items: { type: 'string' } },
  },
  required: ['doc_ids'],
}

const SCHEMA = {
  type: 'object',
  properties: {
    documents: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          doc_id: { type: 'string' },
          directors: { type: 'array', items: { type: 'string' } },
          confidence: { type: 'string', enum: ['high', 'medium', 'low', 'none_found'] },
          note: { type: 'string' },
        },
        required: ['doc_id', 'directors', 'confidence'],
      },
    },
  },
  required: ['documents'],
}

function buildPrompt(docIds) {
  const idsJson = JSON.stringify(docIds)
  return `You are extracting director/board-nominee names from real SEC proxy statement (DEF 14A) text excerpts.

First, run this exact command via your Bash tool to get your assigned documents' text (do not modify the doc_id list):

python3 -c "
import json
ids = ${idsJson}
data = json.load(open('${WINDOWS_PATH}'))
for i in ids:
    v = data.get(i)
    print('--- doc_id: ' + i + ' ---')
    if v is None:
        print('[MISSING FROM SOURCE FILE]')
    else:
        print(v['window'])
"

Then, for EACH doc_id in that output, extract ONLY the personal names of actual board directors or director nominees mentioned in a nominee list, board table, or director-biography section within that document's excerpt.

Rules:
- Only extract names you can actually see in the printed text. Never invent, guess, or complete a name from outside knowledge.
- Do NOT include: committee names, company names, job titles alone, section headers, executive officers who are not also directors (unless the text clearly identifies them as director nominees too).
- If an excerpt does not actually contain a clear director/nominee list (wrong section, boilerplate, false-positive marker match, or [MISSING FROM SOURCE FILE]), return an empty directors array and confidence "none_found" -- do not force a guess.
- Confidence "high" = a clear, apparently-complete board/nominee list; "medium" = plausible but possibly partial; "low" = fragmentary/uncertain names present.

Return one entry per doc_id via the required schema -- exactly ${docIds.length} entries, matching this doc_id list: ${idsJson}`
}

phase('List')
const listResult = await agent(
  `Run this exact command via your Bash tool and return its output as a JSON array of strings via the required schema:\n\npython3 -c "import json; print(json.dumps(list(json.load(open('${WINDOWS_PATH}')).keys())))"\n\nThe command prints a JSON array -- parse it and return it verbatim as doc_ids. Do not omit any entries.`,
  { label: 'list-doc-ids', phase: 'List', schema: LIST_SCHEMA }
)
const allIds = listResult.doc_ids
log(`listed ${allIds.length} doc_ids from source file`)

phase('Extract')
const BATCH_SIZE = 8
const batches = []
for (let i = 0; i < allIds.length; i += BATCH_SIZE) {
  batches.push(allIds.slice(i, i + BATCH_SIZE))
}
log(`${allIds.length} documents in ${batches.length} batches of up to ${BATCH_SIZE}`)

const results = await parallel(
  batches.map((docIds, idx) => () =>
    agent(buildPrompt(docIds), { label: `batch-${idx}`, phase: 'Extract', schema: SCHEMA })
      .then(r => r.documents)
  )
)

const flat = results.filter(Boolean).flat()
log(`extraction complete: ${flat.length} document results returned out of ${allIds.length} requested`)
return flat
