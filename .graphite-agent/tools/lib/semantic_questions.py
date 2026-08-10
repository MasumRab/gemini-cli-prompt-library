from .io import read_json, artifact, LATEST, get_run_id
def generate_semantic_questions():
    conflicts=read_json(LATEST/'semantic_conflicts.json',{'conflicts':[]}); inv=read_json(LATEST/'semantic_inventory.json',{'files':[]}); qs=[]
    for c in conflicts.get('conflicts',[]):
        qs.append({'id':f'q-sem-{len(qs)+1:06d}','type':'competing_symbol_change','symbol':c.get('symbol'),'question':f"Which semantic change for {c.get('symbol')} is canonical?",'options':['merge_semantics_manually','leave_both_blocked'],'recommended_option':'merge_semantics_manually','evidence':c.get('evidence',[])})
    for f in inv.get('files',[]):
        if f.get('generated'): qs.append({'id':f'q-sem-{len(qs)+1:06d}','type':'generated_file_provenance','question':f"Generated file {f.get('path')} changed. How should provenance be handled?",'options':['regenerate_from_source','keep_generated_change_as_intentional','exclude_generated_change','manual_review_required'],'recommended_option':'manual_review_required','evidence':['file matches generated pattern']})
    return artifact('semantic_questions.json',{'run_id':get_run_id(),'questions':qs})
