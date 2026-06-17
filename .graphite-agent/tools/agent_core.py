#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
from datetime import datetime, timezone
AGENT_DIR=Path('.graphite-agent'); OUTPUTS_DIR=AGENT_DIR/'outputs'; DECISION_LOG=OUTPUTS_DIR/'decision_log.jsonl'
EXECUTABLE={'safe','needs_restack'}; BLOCKED={'blocked_merge_commits','manual_triage','cross_root_conflict','unrooted'}
def now(): return datetime.now(timezone.utc).isoformat()
def rj(p,d=None):
    p=Path(p)
    return json.loads(p.read_text()) if p.exists() else d
def wj(p,x):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,indent=2))
def nodes(s): return s.get('branch_graph',{}).get('nodes',{}) or s.get('branch_state',{}) or {}
def snap():
    s=rj(OUTPUTS_DIR/'analysis_snapshot.json') or rj(AGENT_DIR/'analysis_snapshot.json')
    if not s: raise RuntimeError('analysis_snapshot.json missing')
    return s
def plan():
    p=rj(OUTPUTS_DIR/'execution_plan.json') or rj(AGENT_DIR/'plan.json')
    if not p: raise RuntimeError('plan.json missing')
    return p
def append_decision(ev):
    DECISION_LOG.parent.mkdir(parents=True,exist_ok=True)
    with open(DECISION_LOG,'a') as f: f.write(json.dumps(ev,sort_keys=True)+'\n')
def decisions():
    if not DECISION_LOG.exists(): return []
    return [json.loads(x) for x in DECISION_LOG.read_text().splitlines() if x.strip()]
def current_decisions():
    active={}; superseded=set(); revoked=set()
    for e in decisions():
        if e.get('supersedes'): superseded.add(e['supersedes'])
        if e.get('event_type') in {'decision_recorded','decision_revised'}: active[e.get('branch') or e.get('target_root')]=e
        if e.get('event_type')=='decision_revoked': revoked.add(e.get('target_decision_id'))
    cur={k:v for k,v in active.items() if v.get('event_id') not in superseded and v.get('event_id') not in revoked}
    wj(OUTPUTS_DIR/'current_decisions.json',cur); return cur
def nextid(prefix): return f'{prefix}-{len(decisions())+1:06d}'
def relationship_graph(s):
    if s.get('relationship_graph',{}).get('edges'): return s['relationship_graph']
    edges=[]; i=0
    for b,n in nodes(s).items():
        st=n.get('status'); parent=n.get('resolved_parent') or n.get('parent')
        if parent:
            i+=1; edges.append({'id':f'rel-{i:06d}','from':parent,'to':b,'edge_type':'existing_plan_parent','classification':'executable' if st in EXECUTABLE else 'triage_only','confidence':'high' if st=='safe' else 'medium','root_branch':n.get('root_branch'),'evidence':[n.get('reason') or 'derived from existing analysis'],'metadata':{}})
        if st in BLOCKED:
            i+=1; edges.append({'id':f'rel-{i:06d}','from':n.get('root_branch'),'to':b,'edge_type':st,'classification':'blocked' if st!='manual_triage' else 'triage_only','confidence':'medium','root_branch':n.get('root_branch'),'evidence':[n.get('reason') or st],'metadata':{}})
    return {'edges':edges}
def triage_packets(s, rel):
    out={}; i=0
    for b,n in nodes(s).items():
        if n.get('status') in EXECUTABLE: continue
        i+=1; reason=n.get('reason') or ''
        cat=n.get('diagnostic_category') or ('in_target_conflict_resolution_merge' if n.get('status')=='blocked_merge_commits' and 'merge' in reason.lower() else n.get('status'))
        out[b]={'id':f'triage-{i:06d}','branch':b,'status':n.get('status'),'diagnostic_category':cat,'root_branch':n.get('root_branch'),'primary_reason':reason,'relationship_edges':[e['id'] for e in rel['edges'] if e.get('from')==b or e.get('to')==b],'recommended_action':'linearise_before_graphite_tracking' if cat=='in_target_conflict_resolution_merge' else 'manual_review_required','next_steps':[f'explain.py --branch {b}',f'questions.py --branch {b}','validate_plan.py']}
    return out
def questions(triage):
    q=[]; i=0
    for b,t in triage.items():
        if t['status'] not in {'manual_triage','unrooted'}: continue
        i+=1; opts=['leave_triage','exclude_from_migration']
        if t.get('root_branch'): opts.insert(0,'parent='+t['root_branch'])
        q.append({'id':f'q-{i:06d}','branch':b,'priority':'high','question':f'Choose intended handling for {b}.','options':opts,'recommended_option':'leave_triage','confidence':'medium'})
    return q
def summary(s,p):
    bs={}; br={}; idx={k:[] for k in ['safe_branches','needs_restack_branches','cross_root_branches','merge_blocked_branches','unrooted_branches','manual_triage_branches']}
    mp={'safe':'safe_branches','needs_restack':'needs_restack_branches','cross_root_conflict':'cross_root_branches','blocked_merge_commits':'merge_blocked_branches','unrooted':'unrooted_branches','manual_triage':'manual_triage_branches'}
    for b,n in nodes(s).items():
        st=n.get('status','unknown'); rt=n.get('root_branch') or '<none>'; bs[st]=bs.get(st,0)+1; br[rt]=br.get(rt,0)+1
        if st in mp: idx[mp[st]].append(b)
    return {'metadata':s.get('metadata',{}),'counts':{'branches_total':len(nodes(s)),'execution_queue':len(p.get('execution_queue',[])),'manual_triage_queue':len(p.get('manual_triage_queue',[]))},'by_status':bs,'by_root':br,'indexes':idx}
def analyse_outputs():
    s=snap(); p=plan(); rel=relationship_graph(s); tri=triage_packets(s,rel); qs=questions(tri); rec={b:{'branch':b,'recommended_action':('track_and_restack' if n.get('status')=='needs_restack' else 'track_only') if n.get('status') in EXECUTABLE else 'block_or_ask_user','because':[n.get('reason')]} for b,n in nodes(s).items()}
    for name,obj in [('analysis_summary.json',summary(s,p)),('relationship_graph.json',rel),('triage_packets.json',tri),('question_queue.json',qs),('recommendations.json',rec)]: wj(OUTPUTS_DIR/name,obj)
    if not DECISION_LOG.exists(): DECISION_LOG.write_text('')
    current_decisions(); return summary(s,p)
def discover_targets():
    s=snap(); cand={}
    for r in s.get('metadata',{}).get('configured_roots',[]) or []: cand[r]={'target':r,'score':80,'confidence':'high','signals':['configured root']}
    for n in nodes(s).values():
        r=n.get('root_branch')
        if r and r not in cand: cand[r]={'target':r,'score':70,'confidence':'medium','signals':['root_branch in analysis']}
    out={'generated_at_utc':now(),'candidates':cand}; wj(OUTPUTS_DIR/'target_candidates.json',out); return out
def target_analyse():
    s=snap(); discover_targets(); branches={}; qs=[]; rec={}; i=0
    for b,n in nodes(s).items():
        declared=n.get('declared_base'); inferred=n.get('root_branch'); cat='target_confirmed' if declared==inferred or not declared else 'wrong_pr_target_candidate' if inferred and declared!=inferred else 'target_intent_required'; req=cat!='target_confirmed'; qrefs=[]
        if req:
            i+=1; qid=f'q-target-{i:06d}'; qrefs=[qid]; opts=[]
            if declared: opts.append('target='+declared)
            if inferred: opts.append('target='+inferred)
            if declared and inferred and declared!=inferred: opts.append(f'targets={declared}+{inferred}')
            opts+=['leave_triage','exclude_from_migration']; qs.append({'id':qid,'branch':b,'question_type':'target_intent','priority':'high','question':f'Which target should {b} use?','options':opts,'recommended_option':'target='+inferred if inferred else 'leave_triage','confidence':'medium'})
        branches[b]={'declared_target':declared,'candidate_targets':[{'target':x,'confidence':'medium','evidence':['declared/inferred target']} for x in [declared,inferred] if x],'confirmed_targets':[],'diagnostic_category':cat,'requires_user_decision':req,'question_refs':qrefs}
        rec[b]={'recommended_action':'resolve_target_intent' if req else 'keep_declared_target','confidence':'medium','because':[cat]}
    wj(OUTPUTS_DIR/'target_matrix.json',{'generated_at_utc':now(),'branches':branches}); wj(OUTPUTS_DIR/'target_questions.json',qs); wj(OUTPUTS_DIR/'target_recommendations.json',rec); return branches
def root_health():
    s=snap(); targets=discover_targets()['candidates']; roots={}; qs=[]; rec={}; i=0
    for t in targets:
        affected=[b for b,n in nodes(s).items() if n.get('root_branch')==t]; stale=sum(1 for b in affected if nodes(s)[b].get('status') in BLOCKED)>=2
        roots[t]={'health':'stale' if stale else 'current','relative_to':'unknown','diagnostic_category':'shared_root_staleness' if stale else 'root_current','evidence':['multiple blocked/manual branches from this root'] if stale else ['no shared blocker detected'],'affected_branches':affected,'recommended_action':'root_refresh_decision_required' if stale else 'stack_order_allowed','execution_allowed':not stale}
        if stale:
            i+=1; qs.append({'id':f'q-root-{i:06d}','target_root':t,'question_type':'root_refresh_policy','priority':'high','question':f'Many branches from {t} appear stale. How should this target root be handled?','options':['refresh_root_before_stacking','create_clean_integration_base','do_not_refresh_root','leave_affected_branches_triage'],'recommended_option':'create_clean_integration_base','confidence':'medium','affected_branches':affected}); rec[t]={'recommended_action':'root_refresh_decision_required','affected_branches':affected,'next_command':f'root_questions.py --target {t}'}
    wj(OUTPUTS_DIR/'root_health.json',{'generated_at_utc':now(),'roots':roots}); wj(OUTPUTS_DIR/'root_refresh_questions.json',qs); wj(OUTPUTS_DIR/'root_refresh_recommendations.json',rec); return roots
def stack_order():
    s=snap(); rh=rj(OUTPUTS_DIR/'root_health.json') or {'roots':root_health()}; out={'generated_at_utc':now(),'targets':{}}
    for t,h in rh['roots'].items():
        allowed=h.get('execution_allowed'); branches=[]
        if allowed:
            for b,n in nodes(s).items():
                if n.get('root_branch')==t and n.get('status') in EXECUTABLE: branches.append({'branch':b,'order':len(branches)+1,'action':'track_and_restack' if n.get('status')=='needs_restack' else 'track_only','resolved_parent':n.get('resolved_parent')})
        out['targets'][t]={'root_health':h.get('health'),'execution_allowed':allowed,'blocked_reason':None if allowed else h.get('recommended_action'),'stacks':[{'stack_id':f'stack-{t}-0001','branches':branches}] if branches else []}
    wj(OUTPUTS_DIR/'stack_order.json',out); return out
def validate_plan():
    analyse_outputs(); tri=rj(OUTPUTS_DIR/'triage_packets.json',{}); p=plan(); fail=[]
    for e in p.get('execution_queue',[]):
        if e.get('status') not in EXECUTABLE: fail.append({'id':'unsafe-status','branch':e.get('branch')})
        if not e.get('resolved_parent'): fail.append({'id':'missing-parent','branch':e.get('branch')})
        if e.get('branch') in tri: fail.append({'id':'branch-in-triage-and-execution','branch':e.get('branch')})
    rep={'status':'blocked' if fail else 'pass','failed_checks':fail}; wj(OUTPUTS_DIR/'checklist_report.json',rep); return rep
