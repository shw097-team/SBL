from pathlib import Path
import re,json,hashlib,datetime
ROOT=Path("C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG")
OUT=Path("C:/Projects/Agent_Workspace/_r14_packet/raw")
HEAD=re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+)$")
FENCE=re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
REQ=re.compile(r"(?<![A-Za-z0-9_-])(?:SBL-PROP-(?:REQ|ATOM)-[A-Z0-9]+(?:-[A-Z0-9]+)*|D[0-9]{2}-REQ-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)(?![A-Za-z0-9_-])")
ACC=re.compile(r"(?<![A-Za-z0-9_-])(?:SBL-PROP-ACC|ACC)-[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*(?![A-Za-z0-9_-])")
CHILD=re.compile(r"^\|[ \t]*`?(U[0-9]{2}\.[0-9]+)`?[ \t]*\|")
SURFACE=re.compile(r"^\|[ \t]*`?(C-[0-9]{3})`?[ \t]*\|")
CELL=re.compile(r"^\|[ \t]*(POS|NEG|EDGE|SEC|PERF|PARITY|RECOVERY|UPGRADE|ROLLBACK|UNINSTALL|MUT|JOURNEY)/(DETERMINISTIC|STATE_READBACK|PROPERTY|REFERENCE_OUTPUT|STATISTICAL|SEMANTIC_JUDGE|HUMAN|COMPOSITE)[ \t]*\|")
METHOD="Full UTF-8-sig; ATX headings outside fences; partition at every heading; retain nonempty directly owned bodies including preamble. Nonoverlapping review packets, NOT atomic obligations."
files=[]; packets=[]; maps={k:{} for k in ["Cxx contract-family H1 IDs","Requirement/atom ID lexemes","Acceptance ID lexemes","U-child IDs DOC-01","DeliverySurface IDs DOC-00","TQAEP cells DOC-08"]}
for d in range(14):
    doc="DOC-%02d"%d; path=ROOT/("SBL_PIPD-LS-PKG_"+doc+".md"); raw=path.read_bytes(); lines=raw.decode("utf-8-sig").splitlines(); sha=hashlib.sha256(raw).hexdigest()
    headings=[]; fence=None; width=0
    for n,line in enumerate(lines,1):
        f=FENCE.match(line)
        if fence:
            if f and f.group(1)[0]==fence and len(f.group(1))>=width and not f.group(2).strip(): fence=None
            continue
        if f:
            fence=f.group(1)[0]; width=len(f.group(1)); continue
        loc=str(path)+"#L"+str(n); h=HEAD.match(line)
        if h:
            headings.append((n,h.group(2))); c=re.match(r"C[0-9]{2}(?=[｜| :：]|$)",h.group(2))
            if len(h.group(1))==1 and c: maps["Cxx contract-family H1 IDs"].setdefault(c.group(0),[]).append(loc)
        for pattern,key in [(REQ,"Requirement/atom ID lexemes"),(ACC,"Acceptance ID lexemes")]:
            for m in pattern.finditer(line): maps[key].setdefault(m.group(0),[]).append(loc)
        for pattern,key,select in [(CHILD,"U-child IDs DOC-01",1),(SURFACE,"DeliverySurface IDs DOC-00",0),(CELL,"TQAEP cells DOC-08",8)]:
            m=pattern.match(line)
            if m and d==select: maps[key].setdefault("/".join(m.groups()),[]).append(loc)
    assert fence is None,(doc,"unclosed fence")
    bounds=[(0,"PREAMBLE")]+headings+[(len(lines)+1,"END")]; count=0
    for a,b in zip(bounds,bounds[1:]):
        start=max(1,a[0]); end=b[0]-1
        if not any(x.strip() for x in lines[a[0]:end]): continue
        count+=1
        packets.append({"id":doc+":L"+str(start),"doc":doc,"heading":a[1],"source":str(path),"source_sha256":sha,"line_start":start,"line_end":end,"status":"UNKNOWN","status_basis":"NOT_ASSESSED: no packet-specific candidate/implementation/raw-tests/independent-checker join assessed in this source-measurement task; source text is not implementation evidence.","implementation_evidence":[],"candidate_in_scope":True})
    files.append({"doc":doc,"path":str(path),"bytes":len(raw),"lines":len(lines),"sha256":sha,"version_header":"\n".join(lines[:22]),"packets":count,"atx_headings":len(headings)})
units=[{"unit":f["doc"]+" clause-review packets","count":f["packets"],"method":METHOD,"in_scope":True,"status":"UNKNOWN","evidence_source":f["path"]} for f in files]
methods=["Unique Cxx at start of H1 outside fences; globally dedupe exact ID; bundle identities, not predicates.","Unique REQ regex matches outside fences in all DOCs. Lexical subset: mentions, historical IDs and templates may remain.","Unique ACC regex matches outside fences in all DOCs. ID mention is not a distinct acceptance criterion.","Unique CHILD regex first-cell matches in DOC-01 outside fences; dedupe trace/test repeats by exact ID.","Unique SURFACE regex first-cell matches in DOC-00 outside fences; C-ddd is not Cxx contract-family ID.","Unique CELL regex first-cell matches in DOC-08 outside fences; actual allowed class/oracle rows, not declared product."]
diags=[]
for (name,mapping),method in zip(maps.items(),methods):
    item={"unit":name,"count":len(mapping),"method":method,"in_scope":False,"reason":"Overlapping diagnostic; excluded from structural arithmetic, NOT excluded semantic obligations.","status":"UNKNOWN"}; units.append(item)
    diags.append(dict(item,items=[{"id":k,"sources":sorted(set(v)),"status":"UNKNOWN","implementation_evidence":[]} for k,v in sorted(mapping.items())]))
rollup=hashlib.sha256("".join(f["doc"]+" "+f["sha256"]+"\n" for f in files).encode("utf-8")).hexdigest(); stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
ceiling="Unsigned measured inventory and denominator proposal only. D_clause_semantic=UNRESOLVED; atomic semantic total=UNMEASURED. No semantic completeness percentage, FULL PASS, M4 completion, Owner ratification, Native acceptance or release is authorized. UNKNOWN is not absent."
unknowns=["PIPD Source Owner has not ratified this candidate, scope, decomposition, equivalence/supersession, applicability or exclusions. signed=false describes this proposal, not a global signature search.","UNMEASURED: unique applicable atomic semantic obligations; packets can contain compound obligations or non-operative material; Owner adjudication required.","UNMEASURED: implemented/partial/absent product totals; each packet is UNKNOWN because exact subject-bound implementation/evidence/checker joins were not assessed.","Uncoded natural-language requirements and schema invariants are not exhaustively atomicized by REQ/ACC lexical diagnostics.","Orphan-free source-to-atom trace and legitimate exclusions are not established. Active orphan prevents FULL PASS.","Host lifecycle, Native PIPD receipts, SWOF W3 permit and acceptance/release were not revalidated in this proposal."]
data={"schema":"SBL-TS27-DENOMINATOR-PROPOSAL/1","proposal_version":"TS27-DRAFT-1","generated_utc":stamp,"units":units,"total":sum(x["count"] for x in units if x["in_scope"]),"total_kind":"STRUCTURAL_CANDIDATE_REVIEW_PACKETS_NOT_ATOMIC_SEMANTIC_OBLIGATIONS","semantic_total":None,"semantic_total_state":"UNMEASURED","signed":False,"signer":None,"claim_ceiling":ceiling,"unknowns":unknowns,"source_manifest_sha256":rollup,"source_manifest_method":"SHA256 over DOC-ID SPACE lowercase-file-sha256 LF in DOC-00..13 order; final LF included","sources":files,"packet_inventory":packets,"diagnostic_inventories":diags}
summary=Path("C:/Projects/Agent_Workspace/SBL/evidence/source/SOURCE_FREEZE_SUMMARY.json")
pinned=json.loads(summary.read_text(encoding="utf-8")); previous={x["doc"]:x["sha256"] for x in pinned["normative_package"]["docs"]}; match=all(previous.get(x["doc"])==x["sha256"] for x in files)
data["source_summary_comparison"]={"path":str(summary),"all_file_digests_match":match,"claim_ceiling":pinned["claim_ceiling"]}
stdout=["MEASURED_UTC="+stamp]
stdout.extend("DOC="+f["doc"]+" packets="+str(f["packets"])+" headings="+str(f["atx_headings"])+" bytes="+str(f["bytes"])+" lines="+str(f["lines"])+" sha256="+f["sha256"] for f in files)
stdout.extend("DIAGNOSTIC="+x["unit"]+" count="+str(x["count"]) for x in diags)
stdout.extend(["TOTAL_CANDIDATE_REVIEW_PACKETS="+str(data["total"]),"CLASSIFIED_STATUS_PACKETS="+json.dumps({"UNKNOWN":len(packets),"implemented":0,"partial":0,"absent":0},sort_keys=True),"SOURCE_MANIFEST_SHA256="+rollup,"SOURCE_SUMMARY_DIGESTS_MATCH="+str(match).lower(),"SIGNED=false; SIGNER=null; ATOMIC_SEMANTIC_TOTAL=UNMEASURED"])
report=[]
def add(s): report.extend([s,""])
add("# R14-TS27 — unsigned semantic acceptance denominator proposal")
add("**D_clause_semantic=UNRESOLVED. No semantic completeness percentage is authorized.**")
add("## 1. Operational denominator and scope")
add("Product: One Shared Core / SBLM01..06, three separate SP responsibilities, PIPD adapters, HGK/Fabric governed construction and assurance, Host/delivery lifecycle, SWOF dogfood. Sources: exact local DOC-00..13 bytes below. Similar filenames or references to upstream documents do not acquire authority from this proposal.")
add("Final counting unit: one independently falsifiable semantic obligation keyed by authority namespace, source digest and clause span, actor/consumer, trigger/preconditions, one observable predicate, outcome/effect boundary and applicability context. Split compound predicates with distinct failure outcomes, consumers or authority. D is the cardinality of Source-Owner-ratified equivalence classes of applicable atomic obligations. A requirement ID, ACC link, Cxx family, test, source row, installed wheel or delivery surface is not automatically one obligation.")
add("In scope: operative behavioral clauses, schema/ABI invariants, human/Native authority and security boundaries, negative cases, acceptance/Oracle conditions, receipt joins, install/upgrade/uninstall/rollback, cross-domain handoffs and recovery. R/D sections can add requirements beyond C chapters. Every operative source occurrence maps to a ratified atom or individually signed exclusion. Any active orphan blocks FULL PASS.")
add("Out of final D only after recorded Source Owner disposition: pure navigation/physical inventories, non-operative history, duplicate restatements with equivalent predicate/scope/authority, and genuinely inapplicable contexts with signed reason. Preserve aliases and distinct predicates. Examples can contain operative obligations: no blanket exclusion. Blocked-but-required items remain in D; missing permit is not N/A. Research names do not imply installations. Source gaps remain UNKNOWN/open.")
add("Measured candidate unit: one nonempty direct heading-body review packet including preamble. Split at ATX headings outside code fences. Parent introductory prose is retained; tables and fenced examples remain owned by the containing packet; empty heading-only intervals add no unit. No nested-content double counting or silent semantic merge. Packets may contain compound obligations or non-operative material. Their numeric total is review workload, NOT D_clause_semantic. Final atomic total is UNMEASURED pending decomposition, equivalence, supersession and applicability adjudication. Signing the parser count alone does not resolve TS27.")
add("## 2. Measurement command and actual output")
add("Full parser/generator: `C:/Projects/Agent_Workspace/_r14_packet/raw/ts27_measure.py`. Reads complete source bytes; not snippets. Table-key counts are actual rows, not numbers copied from titles. All exact regexes follow.")
add("```text\npython C:/Projects/Agent_Workspace/_r14_packet/raw/ts27_measure.py\n"+"\n".join(stdout)+"\n```")
add("```python\n"+"\n".join(k+" = "+repr(v.pattern) for k,v in [("HEAD",HEAD),("FENCE",FENCE),("REQ",REQ),("ACC",ACC),("CHILD",CHILD),("SURFACE",SURFACE),("CELL",CELL)])+"\n```")
add("Fence closure: same marker, width at least opening width, whitespace-only suffix. Diagnostics exclude fenced text but may retain templates/historical mentions; REQ/ACC are lexical subsets, not exhaustive semantic extraction. Cxx IDs are deduped globally; children/surfaces/TQAEP use selected source documents and exact keys. Diagnostics overlap the packet corpus and are never added together.")
report.extend(["| Unit | Measured count | Included in packet total? |","|---|---:|---|"])
for x in units: report.append("| "+x["unit"]+" | "+str(x["count"])+" | "+("yes" if x["in_scope"] else "no: overlapping diagnostic")+" |")
add("")
add("Historical source-record, different-ID and ACC-link universes named by the round are not adopted as semantic D. Their equivalence is UNMEASURED. JSON total sums only in_scope=true rows, with an explicit structural total_kind. Diagnostic in_scope=false means excluded from arithmetic because overlapping, NOT authority to discard those obligations. All packet source spans and diagnostic ID occurrences are materialized in JSON.")
add("## 3. Status per unit and evidence basis")
add("Every packet and diagnostic item is UNKNOWN for implementation. This is NOT a finding of absent product behavior. This source-measurement task did not assess a packet-specific implementation/raw-test/independent-checker join. JSON.packet_inventory supplies source path, digest, exact interval, status_basis and implementation_evidence=[] for each packet; diagnostic_inventories supplies each ID and exact occurrences. Those are source evidence, not implementation evidence.")
report.extend(["| Unit | Implementation status | Evidence / judgement scope |","|---|---|---|"])
for f in files: report.append("| "+f["doc"]+" packets | UNKNOWN for every packet | `"+f["path"]+"`; per-packet spans/status_basis in JSON; NOT_ASSESSED for subject-bound implementation |")
add("")
add("Implemented requires every applicable predicate to have pinned implementation, genuine consumer/world readback, applicable positive/negative/boundary/security raw results and independent checker. Partial requires evidence for an identified proper subset and explicit gaps. Absent requires positive evidence of missing required applicable behavior on the exact candidate, such as a controlled failing case with asserted expected outcome. No adequate evidence or no assessment = UNKNOWN, never absent. CLASSIFIED_STATUS_PACKETS counts classifications in THIS proposal, not product failure totals.")
add("Evidence read: `C:/Projects/Agent_Workspace/_r14_ev/_governance/round-20261022-r14/SBL_R14_EXECUTION_STATUS.md#L65-L71` is an earlier checkpoint recording semantic denominator UNKNOWN / Source Owner unsigned, not a fresh full-product verdict. `C:/Projects/Agent_Workspace/SBL/evidence/source/SOURCE_FREEZE_SUMMARY.json#L81-L82` limits its freeze to local bytes, not Owner-approved SourceFreeze; file digests were freshly compared above. `C:/Projects/Agent_Workspace/SBL/evidence/EVIDENCE_MANIFEST.json#L1-L12` is a file manifest, not an obligation-to-implementation closure proof. Existing code or global test totals do not establish packet implementation.")
add("Required evidence chain per ratified atom: source clause -> semantic predicate -> implementation symbol/path -> test/Oracle -> raw receipt with exact subject/candidate digest -> independent checker -> Owner decision. Stale/foreign subject evidence cannot advance status. No product runtime tests were executed in this proposal.")
add("## 4. Concrete Source Owner signature block — deliberately unsigned")
add("Before signing an OFFICIAL denominator, materialize the reviewed atomic ledger and every source-packet disposition, equivalence/supersession decision and legitimate exclusion. Bind exact bytes in an external signed receipt. Approval to review this proposal alone is not denominator ratification or product acceptance.")
add("```text\ndecision_kind: OFFICIAL_SEMANTIC_DENOMINATOR_RATIFICATION\nproposal_version: TS27-DRAFT-1 (or named reviewed successor)\nsource_scope: exact SBL_PIPD-LS-PKG_DOC-00..13 snapshot below\nsource_manifest_sha256: "+rollup+"\nmanifest_encoding: DOC-ID SPACE lowercase-file-sha256 LF; ordered DOC-00..13; final LF\nfinal_proposal_json_sha256: TO_BE_COMPUTED_BY_SIGNER_FROM_FINAL_BYTES\nratified_semantic_ledger_path_and_sha256: UNSUPPLIED\nequivalence_supersession_ledger_sha256: UNSUPPLIED\napplicability_and_exclusion_ledger_sha256: UNSUPPLIED\nsource_doc_versions: exact headers in JSON.sources plus manifest digests; Owner confirms\natomic_semantic_denominator: UNMEASURED / NOT_RATIFIED\nproduct_kind_mode_host_risk_profile_permission_scope: UNSUPPLIED\nsource_owner_name_principal_organization: UNSIGNED\nsource_owner_authority_basis: UNSIGNED\ndecision_date_time_with_timezone: UNSIGNED\nassertion: every operative clause maps to a ratified atom or signed exclusion; no silent orphan\nsignature_or_verifiable_receipt: UNSIGNED\nchange_rule: changed source/applicability/ledger bytes require new ratification\n```")
add("No artifact self-digest is embedded: external receipt binds final JSON and reviewed ledger bytes. Source Owner signs denominator truth, not Native permits, independent acceptance or release. Today signer identity/authority, decision date, atomic count/ledger, equivalence, applicability/exclusions and signature are unsigned/unprovided. No agent may fill them as Owner. signed=false states this candidate status, not a global signature-store search.")
add("## 5. Exact claim ceiling today")
add(ceiling)
add("Allowed: source-bound review workload, lexical/table inventories, unsigned definition, explicitly scoped artifact observations and UNKNOWNs. Prohibited: any semantic completeness percentage, including a zero-complete percentage inferred from UNKNOWN; FULL PASS/M4 closure; all requirements implemented/absent; Owner-approved denominator/SourceFreeze; Native acceptance, world-effect permission or release. After denominator signature, a percentage still needs a separately evidence-validated numerator over exactly the same scope; this proposal provides neither that numerator nor product acceptance.")
add("## 6. Reproducible source snapshot")
add("Measured UTC: "+stamp+". Version identity is exact file bytes/digest. JSON.sources includes opening version/header text. Source root: `"+str(ROOT)+"`.")
report.extend(["| DOC | bytes | lines | SHA256 |","|---|---:|---:|---|"])
for f in files: report.append("| "+f["doc"]+" | "+str(f["bytes"])+" | "+str(f["lines"])+" | `"+f["sha256"]+"` |")
add("")
add("## 7. Unresolved work and side effects")
for u in unknowns: add("- "+u)
add("Only ts27_denominator_proposal.md, ts27_denominator.json and retained ts27_measure.py are written under requested raw output directory. Source DOCs, product repos and existing round governance artifacts are not modified. No self-acceptance, Owner signature, runtime product test or official denominator is issued.")
OUT.joinpath("ts27_denominator.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
OUT.joinpath("ts27_denominator_proposal.md").write_text("\n".join(report)+"\n",encoding="utf-8")
print("\n".join(stdout))
