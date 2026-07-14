# Provenance and Statement of Authorship

**Works:**
- *The Architecture of AI Agents and LLM Systems* — the book (`book/`, and the HTML/PDF built from it)
- *Practicum: AI Agents by Hand* — the companion course (`course/`, and the HTML/PDF built from it)

**Author:** Aleksandr Drobiazkin <aleksandr.drobiazkin@gmail.com>
**Contact:** LinkedIn https://www.linkedin.com/in/aleksandr-drobiazkin-501bab263
**This revision fixed:** 2026-07-17 (UTC)

Copyright (c) 2026 Aleksandr Drobiazkin. Licensed under CC BY-SA 4.0 (prose, figures, diagrams)
and MIT (code samples and `tools/`) — see `LICENSE`, `LICENSE-CODE`, and `NOTICE`.

This file records the SHA-256 hashes of the exact state of the manuscripts on the date above.
External evidence of that date: OpenTimestamps attestations (`*.ots`) anchored in the Bitcoin
blockchain, plus this repository's git history.

**What that evidence proves, precisely.** A timestamp attestation proves one thing: a file with
the recorded hash existed no later than the attested Bitcoin block. It is evidence of **date**,
not of authorship. It does not establish who wrote the work, that the work is original, or that
no one else held the same file earlier — it bounds the date from above, not from below. Its
practical value is narrow and real: it defeats the claim that the text was written after the
fact. Authorship rests on the author's assertion below and on the record of composition, not on
the blockchain.

## Original language, translation, and the bilingual edition

**These works were written in Russian and translated into English by the same author.**
The English text is not a third-party derivative; it is the author's own translation of his
own work, and both language versions are covered by the same copyright.

**Tools.** AI tools were used in the making of this repository — the prose of both editions,
and the code alike. An assistant (Claude, Anthropic) reviewed drafts, flagged errors and
inconsistencies, and proposed alternative wordings. Every claim, every decision about
structure, every source, and every sentence as published was chosen, written or rewritten, and
verified by the author, who takes responsibility for all of it. The model is a tool, not a
party: it holds no authorship and no rights. See `NOTICE` for the full statement, including
what the licenses do and do not convey where a part is not protected.

This repository ships **both editions**: the English edition at the top level and the Russian
edition under [`ru/`](ru/) — both are hashed in the SHA-256 block below. The Russian sources
also live in the author's separate working repository, where their **dating** is established
independently by earlier OpenTimestamps attestations: the first on **2026-07-04**, confirmed in
Bitcoin blocks **956678–956738**, with the stamped files recoverable from that repository's
first commit (`d0bbf7b`). The English edition is later; its attestation is this manifest's own.

Priority rests on those block heights, and deliberately not on any date in either repository's
git history. A git date is self-reported: `GIT_AUTHOR_DATE` sets it to whatever you like, a
rebase rewrites it, and this repository's history is squashed to a single commit — so its dates
are worth nothing to anyone who cares to dispute them, and they are offered as nothing. Block
956678 cannot be moved, backdated, or rewritten. That is what carries the priority of the
Russian original.

This manifest establishes what the files are. It does not establish when they were written,
and it does not need to.

## SHA-256

```
# The book — sources (English edition)
d918d01a613f6729a5833b6771cba3ab49f48757bd24ccff4b48118d7fbd6a05  book/01-language-model-as-component.md
ad9b7aa8db8d83a61ffdc21c2f6fcb31bfcaa64dcfef354620c9e46b6d69f498  book/02-economics.md
2199f408cc408d2f55788028e185f8de51e592004b08906ffcc2ab058d2e6d1b  book/03-prompt-engineering.md
9b4fcc27d74451629024dff28d77f7cc44447e4c649999138d36d2b05a75f88d  book/04-context-engineering.md
a4e8054ba2b33c14d1b668aa0236aa083c12bbbd0f89589eb87e76042a0d249c  book/05-structured-output.md
f59dd912c55430340e7aa49e1406e8cd612c61ba163964ce66fd530407c905d7  book/06-rag-introduction.md
f36392c15be0a8eae34613e8e33f68c079554b7eb4848254c71cfa755f46e581  book/07-retrieval-patterns.md
00813c7357fa77d609eb776fc77f01ebe59ba294dcbd3793581792f01fd24e50  book/08-vector-indexes.md
0639228ff85f25ebb231bc580adedf18612ebc4fae47c85a4f0be1a3e1d602cc  book/09-rag-evaluation.md
417a1ba325cb2240931628fbc22c92dba55c9b6bf97bc36d90fa93f2257ec2bc  book/10-agent-as-distributed-system.md
55c7744f89f212392320c0a8f08f1cd4ad932ef54ca2d4fc44c25f4cd3eb2754  book/11-agent-patterns.md
240913e7345ca034e5424fbc9abab9db58362c8642f61b0257f89e7cdbacdecb  book/12-tool-calling.md
2a7686260a0ec7bda25ba47614f80ac4c6fb883db79f1b1971cdb897d3c0d95b  book/13-memory-and-reasoning.md
5afdaab4b2bd0886e3d5d518675258bb125d589ff77120e950ebad80663a7399  book/14-multi-agent-systems.md
ddd10f71f235b0d177c12a6e519ea39204b10fc4481fbc5fe7386ef0be540d97  book/15-mcp.md
719dc763f296ca6ae6014a30356e1a195a34b83e293dc45ca2159763c8423ab7  book/16-jvm-stack.md
900e21dd3fad65ef3c0d2ebb600e927d25bd5997bb0aa991a044b24390f7c8a8  book/17-evaluation.md
dc298af07fd5617aac0290cc78ea71afaa1e06a46e4d03acdf45c9198c593fbb  book/18-observability.md
1df607d9fdde41271e265299f86dd58d1a429f9bb073f243ef3f3c559ae062df  book/19-security.md
ff5a0cb47ed02b89f8abf56782601cce80280f6bbf9baf50dfc5c9cd675da542  book/20-cost-and-latency.md
83e5d4ddcfc1ed92befa55f8355c9a8080f6150221b1d2ce87d7a24028491ee1  book/21-fine-tuning.md
b388adbbf824146814eff637ee2ddd6feecec4f92d75686e4be3c6034f71b949  book/22-serving-open-models.md
263b54e5002a52853387f472751203a93fcc8e348bc6b3844072d5882742d3eb  book/23-pre-training.md
58db2e9401ff8fd1dc24597233111ca7ded15c994beaf2604a0aba229c15eb69  book/24-reference-architecture.md
31766056860611b6d90e5a5fcbccfbb8585a614d1ee16175f760f860483d4eb2  book/25-organizational-adoption.md
a7c57b257b99ea88ca5f98c402e0bf16b2d496a788f0c509b01cfc2dc1205ba7  book/26-worked-example.md
6fd6c97bef9c014e0f2585f28273c0ea6f21b03759e57bb2f33a315b4bb2ea49  book/appendix-a-linear-algebra.md
0e1e42132edfb02b8c494584c45ab32bb763ff28b6ec7eab880438ad5c9e73a8  book/appendix-b-pattern-index.md
1bdf37d62b883151f2dcab1d5d7dd15411e331e5fb7b1432cdc3d54ead3af4ea  book/appendix-c-trajectory.md
87ebcfb2b46e4cdc10aff1531301d519a6b7768156aa292232db4115ee2cc474  book/appendix-d-preflight-checklist.md
9176ec3fe52158206df061548d4aa29eb85b01bee6b7c28fcf615e3ce7f666b9  book/appendix-e-bibliography.md
ae4a63a2e7e1590e2edbb332d9755b618d69ce591685dfd9bdd6415266b46810  book/front-matter.md
49672716a34d9c3b871bfa56ddf43a8f7e359151fe8b4b854fa2a577391fc511  book/glossary.md
609037a6fafe711c1a6a249e4dfeef48888414e528564c26ca878c3d34113e71  book/toc.md

# The course — sources (English edition)
cca9fed8c598c57b16a3ea43f1e9741755ae40a97d503bdf7bf9c942fdb62d51  course/README.md
26e8ba3a5f55968076c042341a48665f34e28a92d89c2c7be424d9076b671fa9  course/module-0.md
f60dd6485f25ee773a12682478dc4ca9acb8e301bf3e7f29906ff34c134d2bed  course/module-1.md
013c9b10521566a45992013becd3dd767f229f792a66614ea8c3291e4926eeef  course/module-2.md
39af7c50211503a5e6e62cb000016994bb6135471fc2f0f8b471df17d4ad7f97  course/module-3.md
60462c23fd3c12811f3724944a14bb84ab07e173ad40760b45b61b5486a8aa0b  course/module-4.md
9b984dd1f8aac7c015adf13d1b67820e2e64d0ae7db6f8819a7cc32f2be6fc08  course/module-5.md
ec382567e8cb97bd0fadc11cc6596871f2d71add1c7bb386a2ca3d97adc9d1a6  course/module-6.md
7eba043d731e9ed72e685303b3434e0805a06a5428df81f8052fb12ca79273e4  course/module-7.md
015c9ea80e6ab4972863dbbccedfdf093827e1dbb392c5df53adf2f2f14fa4b7  course/module-8.md
f928a3ec3285a8be8a4bbcdecceadffb732c1ad4a211ebae2e991a552836827e  course/python-primer.md

# Figures (English edition) and the scripts that generate them
e65eca5204b8e4063966903e3d742c5c06048ad4ba5dc6378288165b9c6cecda  book/images/fig_attention_complexity.png
58e53463f53d3eccfcf641b720a3a7c8b6da2e393be3ebbaad1e9c0029521c2d  book/images/fig_batching.png
8c26e3bf7972ecd5f248fa3691e2450ff4b286b4d272bf430202193ddbe633d4  book/images/fig_breakeven.png
19f5a29875d3f2328c7e543a509b253adc9c4f00ef465f0edc77ce1d1db07ecc  book/images/fig_context_ucurve.png
acd9c309500160acb4131764451d1408b580de07701c250f8c5279cbe451ed62  book/images/fig_cost_levers.png
c040b9aeb640234e077a008de53cf219898f6c54a9c2bf6758a5d0b51c1315d4  book/images/fig_distillation.png
729a81648746fdd61171afc384d43ec78ea89615f1bbf55e89e7c679ec1733ec  book/images/fig_injection_attempts.png
e11e85441f28d1598717bc0b16b52685f4de1581163aa4108ce69a22c4dccd61  book/images/fig_isoflop.png
138df86eeef888316984b2786ec0532c0e6aa5c2111a6ebec0e478cd5c9b4a13  book/images/fig_kronecker_rank.png
f9fc44a19f53fc390a388c99be9e16faad0fb2d0bb8af69a587103eb76c7b9e3  book/images/fig_kvcache_growth.png
12190e98b02e362cb4b2186b185a937ca910972d7a3a9183d3714856af6aa2be  book/images/fig_lethal_trifecta.png
239b1455701894d6dbaa88ea4508247c823a14b99203099b99feb4e1c114ec8d  book/images/fig_lora.png
b89a6a2fcea0f1c024650fa330c42623c2bfda24afd50212445e3a2328b779d6  book/images/fig_mast_failures.png
4d5d7da9d7d6e87fb3c53a93fd32b960e059bcc05ac34482582a7f47831a92ed  book/images/fig_mcp_nxm.png
439ce0f37493128188586d99e8570a25fc5fba13aba964bab9e14b1e1d649b5d  book/images/fig_multiagent_tokens.png
96b00512ab10db8ab4fc54ed7580f74ad1241854df73a52b95839636a3edf207  book/images/fig_rag_two_axes.png
3f8f73d0eb13d4a14ec4be05f77acce5c5ca9b89c972acffa5c799b8ffa0e6c7  book/images/fig_temperature_softmax.png
db07919d3565a6d1a7de6adb767508e92bd2878ee8574ee31df8030747f05656  book/images/fig_test_time_compute.png
cb9d042a486c49c09fdca4d31e1fa977dc724131a3d8399b657d792fa335d945  book/images/fig_tokens_per_param.png
0ca499d2fa460820d3676fcf1180a3c32b7c1f2f5a9f01c59457b36c92116b1b  tools/figures/fig_attention_complexity.py
c14e9d2bb689c798207529ac8df223bcba352a2b78dae3c07e8c9ab8cee1f7aa  tools/figures/fig_batching.py
8906336bbde9ce362cde425d0b3618a08ef2ce3e39967cc25dea209f2c51bd71  tools/figures/fig_breakeven.py
7f61b0525de7f22dc579592df11b9c5c49b7372905089672a32baf3fd1d89530  tools/figures/fig_context_ucurve.py
ae4362b0d4c7089df59c62c594166f0cf7591bbbd80f910233a779b89f58a34a  tools/figures/fig_cost_levers.py
a15b5d6a88c376f0b090ce6ca8b2697dc352603fdc75f6f40a8b695a276a14d5  tools/figures/fig_distillation.py
71b166c866a16bdc16acb1a81c470031857ff8ca34ce87016ebfea03c6875b07  tools/figures/fig_injection_attempts.py
387d9724fdadc110b9634d32391ae73ed2330a9665b6fbfe001ddca8f50b803c  tools/figures/fig_isoflop.py
e2e7ef0f949f1a1ca126c07fce37e8a5fb22c881eedde1044ba6cf68869bb5bb  tools/figures/fig_kronecker_rank.py
a5ae743a4399d5fb3e6f1199c15de15e4f13d8696b6eff37bd6d0429b67bb638  tools/figures/fig_kvcache_growth.py
33c4d1d027d790f88e72e7df804f6061318eccf09042ee6c76ea47c94452395e  tools/figures/fig_lethal_trifecta.py
4984e3497af38321442254f2bcb4515fe0212dd30dc03016db1b74d21834eac8  tools/figures/fig_lora.py
c84446d023b98da478c004f38ac4cd2c3dc8e998f7004b5653dcc9bb538b447c  tools/figures/fig_mast_failures.py
a1c3f5165d8df0a023f498c27ed382b91579df33e743c9d5a72d44bc992f8949  tools/figures/fig_mcp_nxm.py
bcfa3bd619d285e393e6d53ae28ca2e45385bcfa227898248e659a96cefd248a  tools/figures/fig_multiagent_tokens.py
9247c874497218e749974eb17b16a1f10d17e44cce8afd6e7584baf85d05fe92  tools/figures/fig_rag_two_axes.py
791f654a18ec71980c1306c379ca862d6a72976066584ed800a16139375eebcc  tools/figures/fig_temperature_softmax.py
2688d71840f00be5d19413e1fa2442b1c5db201d881a5ee294304d27ab0d7e5a  tools/figures/fig_test_time_compute.py
669fedcf76bd186a619a3861d258185c5afaf662acea1389029ff0e61bedf8b8  tools/figures/fig_tokens_per_param.py

# Built artifacts (English edition)
3891c33d813abcf0e4790854abad3858d49bcb35c47a12c9b9162108161a6901  ai-agent-architecture-book.html
9252fc462eb95d62db8a807be887e195fae52acb59152082b4447a1fbf8b86af  ai-agent-architecture-book.pdf
891c31d82bfb525ff33f3b396e8fdd35a553508b3657380cd3e28fc45cc245ed  ai-agent-practice-course.html
07035c92b4c69dd797605b2cdfc80060ae8ef0ea4f53860a4170afe0a6942324  ai-agent-practice-course.pdf

# Repository documents
887833ef346adb07cddbf201da19219fac8b5123d6a44aefe2d140cd594ad12c  README.md
e4d1b44d5412dad8582f0e81adf4c4819c40ed7742d0a4111db83c698bb842e4  NOTICE
5f399b87aa4b25cc02c72212ab6acd0a97abad1b0d26daac48381ebb1776fc4f  CONTRIBUTING.md
28a9529c7d0bb4dc51f4bf5c116a3d16ef247a052f7591466768ddf563fd1cf5  LICENSE
a1dcdefd977ece7328366f28c355be9ee49b07b017377bd2c218c2f146b62fa0  LICENSE-CODE

# The typesetting pipeline
f79b2ddbdf98767b74f329cf7e4925d12ce2065dca88fcdde13ac7dca63d1a13  build/build.js
50889a0ba6dee6ebc0190730235cfa481a0ede6a80ad42e17634b9b36a3b5e44  build/render-pdf.js
265e64866442bf7a9bc01371d23613d3bece8ce779b1d8bc89fdb69122f8603c  build/book.css
f641f3ccd97027273b2c09ab50a2a45ed2c94adb25388e1595137f576543e610  build/package.json
4d8827b6b90b47621e97f4c64c110d07cef160beeebb95197cfa6473f3770240  build/package-lock.json
57b64b5f061b66b8bad22b4b7aed72c2bf16d48ad954fd1e82384ace915a7b06  build/README.md
5b37e8f12633a520a9c5ba7fa56e40dc8fa5b2b20fe0a5e04fe4b08bb749f27a  build/third_party/KATEX-LICENSE

# Russian edition — sources, figures, and artifacts
bfda78e7af71b8ac7230020ad953d2ad47a8d6226a8368e5e3b08a6b4cec8a5d  ru/ai-agent-architecture-book-v2.md
d2e0c91afced82ced1547b90dd5defd88084c3dad334017ec5d38f56316907cc  ru/ai-agent-architecture-book-v2.html
f0ae3f9107b72b8eddc8026d2bdbe730a21da93d3d9c27e3f91e3233e6b62a75  ru/ai-agent-architecture-book-v2.pdf
d4b062fc7990e5e0bafcc745299ef3e05d946a201cbd3e87a0f3991106c4c98f  ru/ai-agent-practice-course.md
a83cfd41ca7af140ed25534efc0bc36f97bb7cc6e45a6750627d1c812f418cb3  ru/ai-agent-practice-course.html
a02892c898843c2f7ade3550bda8152e7b8a1813685fe4db14fb698b5c8d61a2  ru/ai-agent-practice-course.pdf
379e154cc6d16d71c167926b04bfc1457ebeeb41a3fef91b11c60a5174b181b6  ru/course/module-0.md
205855ef17cefb70237a85133ed76ed4cd72a009e3e56236230efdd7f259cf4a  ru/course/module-1.md
328a6ed250b4770dcf7aa2843f695d889aeeb62c5f92e3918046e06681f99623  ru/course/module-2.md
f041f8b2ce37c5818e75a37446fcbee1b7b2ba0eba5cb514284ceed88fc9e812  ru/course/module-3.md
44878eafdb635a56d259c96c0585703f635bc83d0770097cacf2406932ee188b  ru/course/module-4.md
8f6f14cd3ba0862162de38aca93c88fba87ba33ab47f3f8b3b4d6e0bf076998e  ru/course/module-5.md
d4fac8f9efb37cb2ccb2a18bcfb0d326cc405eb3d01cc393d7cbdcc8a617ec62  ru/course/module-6.md
e2dd74d06a4be4c14369cd74d7de3208a056ae3cbb82ec62054ba942c6f4152c  ru/course/module-7.md
d32c0e1042a97802a923897637b712d64b5d1b571c75f9ef1e24f8b1b8c4a65d  ru/course/module-8.md
d1690df27f689c0d3df244a4957d13300b0e15fbfa1c18731de43d88f4bdc231  ru/course/python-primer.md
198e3658a791960d0489fe8410f38baff48dcf489940d8a31e4bb6b804f55c11  ru/images/fig_attention_complexity.png
8a3d202fafbf6ebb902157d262a01953cc5ce311b486e3b5fb7fcab4514fce3c  ru/images/fig_batching.png
2db07e9d50600d4043bd6eab3b1c83d1b963951e27f1b793102c41342d89d6d6  ru/images/fig_breakeven.png
fa069adb5402a990015965b9e05427e303b1ebbeeabb4169e9c7c9d967452706  ru/images/fig_context_ucurve.png
a0b88c62f33ab193eaa47b905d94d2550908a71e10f7dcd692f8c9a813e5dab7  ru/images/fig_cost_levers.png
fb33d4dadf1bc17d342026f3793b6189a28ed8701a23e3f46b5d596dab863a46  ru/images/fig_distillation.png
402d435db63729c772e0e69b48821fd6cd6e84e946ebcec19ad682b8cec4281e  ru/images/fig_injection_attempts.png
e573134973426305ac0aa76ca72332bcb15bd611a9fa5e4512e3024d83458db1  ru/images/fig_isoflop.png
6a3969c43f32d99e8dd5ae93d406b780e936fee06dae81061eb2ca56e696ebfc  ru/images/fig_kronecker_rank.png
d923128c6586f297eaecbca4ce0a05b6ad399b1e4b0c654bd6ecf384f355e970  ru/images/fig_kvcache_growth.png
db976d0b43edc23c6753f83ad0a3ec922318a9c975cc99fe9e374bc2a236a8c3  ru/images/fig_lethal_trifecta.png
e0b76a8f629394c378d912f900ce77662e6f5f8048273be677201d0d7fc0b0f9  ru/images/fig_lora.png
ee2f35d1beb841a4cd437d009ebfa4c828655d6e5217ca95a3c227075c1905c4  ru/images/fig_mast_failures.png
8f974e44d22e04df15f8a150c9b02cf3da45f60e274555a443e3a4be05d71960  ru/images/fig_mcp_nxm.png
b6913871f9dfdda329f1cf608fe5d2fbc35fc3f44db051518195d2102fc29615  ru/images/fig_multiagent_tokens.png
6140ad04ed7f7280b883412e5d5302b3bbbbe1497808a18cb20de6364f710bbb  ru/images/fig_rag_two_axes.png
61312a9db723edb23b56fd4dc47be4e6fa4924b983bbbe4bdc1f16df920141e6  ru/images/fig_temperature_softmax.png
c2fbd772d1610c7a55dd5ae9430ce7aa23f349a25f45a8b8e80a40a41ccfe325  ru/images/fig_test_time_compute.png
394ae484c66348fd88c31b53636cfb2cfff1b0074a96dea028476824b4b34f54  ru/images/fig_tokens_per_param.png
```

## Verification

```bash
# every hash in this manifest
shasum -a 256 -c <(sed -n '/^```$/,/^```$/p' PROVENANCE.md | grep -E '^[0-9a-f]{64}')

# the timestamp (requires opentimestamps-client: pip install opentimestamps-client)
ots verify PROVENANCE.md.ots
```

A `pending` status means the attestation has been submitted to the calendars but is not yet
in a Bitcoin block; it proves submission, not the date. Run `ots upgrade *.ots` a few hours
after stamping to pull the confirmed attestation.

## OpenTimestamps

- **2026-07-17** — this revision: `PROVENANCE.md.ots` covers this manifest, and this manifest
  covers every file listed above by hash — the manuscripts of both editions, the figures and
  the scripts that generate them, the typesetting pipeline, and the built artifacts. Individual
  files are not stamped separately; the manifest's stamp covers the set.

  A stamp is **pending** when first made: it proves submission to a calendar, not a date. It
  proves the date only once a Bitcoin block confirms it — and this file cannot name that block,
  because naming it would change this manifest's hash and void the very attestation named. So
  `ots info PROVENANCE.md.ots` is the authority on the current state, not this sentence. To
  confirm a fresh stamp: `rm -f PROVENANCE.md.ots.bak && ots upgrade PROVENANCE.md.ots`, then
  commit the upgraded file. Both halves matter. `ots upgrade` writes its backup first and
  aborts if a stale `.bak` is in the way — while still printing that it fetched attestations,
  so it reads like success and writes nothing; trust the exit code, not the output. And an
  upgrade that is never committed is evidence thrown away: it cannot be regenerated, because a
  new stamp starts the wait over and says nothing about the older state.

- **2026-07-04** — the Russian sources in the author's separate working repository: the first
  attestations, confirmed in Bitcoin blocks **956678–956738**. That chain is what establishes
  priority of the Russian original over the English edition.

## Reproducing the artifacts

The HTML and PDF in this repository are built from the Markdown in `book/` and `course/`;
their hashes are listed above so that a reader can confirm the shipped artifacts correspond
to the shipped sources. See `build/README.md` for the exact commands.
