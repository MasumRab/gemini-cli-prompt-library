from __future__ import annotations
import argparse, json
from .io import artifact, text_artifact, read_json, LATEST, get_run_id
from .git_core import GitCore
from .symbols import semantic_inventory, ast_index, symbol_graph
from .references import reference_graph
from .semantic_conflicts import detect_semantic_conflicts
from .semantic_questions import generate_semantic_questions
from .semantic_recommendations import semantic_recommendations, validate_semantics
from .task_tracker import export_todos

# Wrapper functions to handle args parameter for functions that don't expect it
def semantic_inventory_wrapper(args=None):
    return semantic_inventory()

def ast_index_wrapper(args=None):
    return ast_index()

def symbol_graph_wrapper(args=None):
    return symbol_graph()

def reference_graph_wrapper(args=None):
    return reference_graph()

def detect_semantic_conflicts_wrapper(args=None):
    return detect_semantic_conflicts()

def generate_semantic_questions_wrapper(args=None):
    return generate_semantic_questions()

def semantic_recommendations_wrapper(args=None):
    return semantic_recommendations()

def validate_semantics_wrapper(args=None):
    return validate_semantics()

def export_todos_wrapper(args=None):
    return export_todos(getattr(args, 'backend', 'internal'), getattr(args, 'dry_run', False))
STAGES={'discover':{},'semantic-inventory':{},'ast':{},'symbol-graph':{},'reference-graph':{},'semantic-conflicts':{},'semantic-clarify':{},'semantic-recommend':{},'validate-semantics':{},'recommend':{},'command-plan':{}}
def discover(args=None):
    g=GitCore(); root=g.root()
    if not root: raise SystemExit('Not inside a Git repository')
    return artifact('repo_inventory.json',{'run_id':get_run_id(),'repo':{'git_root':root,'current_branch':g.current_branch(),'is_dirty':bool(g.status_lines())},'state':{**g.active_state(),'conflicted_files':g.conflicts(),'status_porcelain':g.status_lines()},'branches':{'local':g.local_branches(),'remote':g.remote_branches()},'targets':{'configured':[],'origin_head':g.origin_head(),'discovered':[g.origin_head()] if g.origin_head() else []}})
def topology(args=None): return artifact('topology_graph.json',{'run_id':get_run_id(),'nodes':{},'edges':[]})
def replay(args=None):
    g=GitCore(); high=any(g.active_state().values()) or bool(g.conflicts()); return artifact('replay_risk.json',{'run_id':get_run_id(),'branch':g.current_branch(),'summary':{'overall_risk':'high' if high else 'low','execution_allowed':not high},'repository_state':{**g.active_state(),'dirty_worktree':bool(g.status_lines())},'conflicts':{'conflicted_files':g.conflicts(),'conflict_markers_detected':[]}})
def recommend(args=None):
    qs=read_json(LATEST/'semantic_questions.json',{'questions':[]}); todos=[{'id':f'todo-sem-{i+1:06d}','status':'open','priority':'high','description':'Resolve semantic question '+q['id'],'question_ref':q['id']} for i,q in enumerate(qs.get('questions',[]))]
    artifact('agent_todos.json',{'run_id':get_run_id(),'todos':todos}); return artifact('agent_work_package.json',{'run_id':get_run_id(),'status':'blocked' if todos else 'ready_for_validation','todos':'agent_todos.json'})
def command_plan(args=None):
    sem=read_json(LATEST/'validation/semantic_validation.json',{}); blocked=sem.get('status')=='blocked'; return artifact('command_plan.json',{'run_id':get_run_id(),'mode':'dry_run','execution_allowed':False,'blocked_by':['validate_semantics'] if blocked else [],'commands':[]})
def report(args=None):
    qs=read_json(LATEST/'semantic_questions.json',{'questions':[]}); return text_artifact('semantic_clarification_report.md','# Semantic Clarification Report\n\n'+'\n'.join('- '+q['id']+': '+q['type'] for q in qs.get('questions',[]))+'\n',report=True)
def all_cmd(args=None):
    discover(args); topology(args); replay(args); semantic_inventory_wrapper(args); ast_index_wrapper(args); symbol_graph_wrapper(args); reference_graph_wrapper(args); detect_semantic_conflicts_wrapper(args); generate_semantic_questions_wrapper(args); semantic_recommendations_wrapper(args); validate_semantics_wrapper(args); recommend(args); command_plan(args); report(args); return read_json(LATEST/'command_plan.json')
def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('--local-only',action='store_true'); p.add_argument('--dry-run',action='store_true'); p.add_argument('--backend',default='internal'); sub=p.add_subparsers(dest='cmd',required=True)
    for c in ['discover','topology','replay-risk','semantic-inventory','ast','symbol-graph','reference-graph','semantic-conflicts','semantic-clarify','semantic-recommend','validate-semantics','recommend','command-plan','report','export-todos','all']: sub.add_parser(c)
    a=p.parse_args(argv); funcs={'discover':discover,'topology':topology,'replay-risk':replay,'semantic-inventory':semantic_inventory_wrapper,'ast':ast_index_wrapper,'symbol-graph':symbol_graph_wrapper,'reference-graph':reference_graph_wrapper,'semantic-conflicts':detect_semantic_conflicts_wrapper,'semantic-clarify':generate_semantic_questions_wrapper,'semantic-recommend':semantic_recommendations_wrapper,'validate-semantics':validate_semantics_wrapper,'recommend':recommend,'command-plan':command_plan,'report':report,'export-todos':export_todos_wrapper,'all':all_cmd}
    out=funcs[a.cmd](a); print(json.dumps(out,indent=2) if not isinstance(out,str) else out)
