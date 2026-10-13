import asyncio
import pytest
from src.state.history import ConversationHistory
from src.state.fact_store import MemoryCandidate, MemoryExtraction, FactStore, canonicalize, validate_extraction
from src.state.privacy import guarded_run


def candidate(value='Python', **changes):
    fields=dict(source_id='s1',source_text=f'I prefer {value}.',decision='store',category='preference',
        key='preferred_programming_language',value=value,confidence=.99,reason='explicit fixture')
    fields.update(changes)
    return MemoryCandidate(**fields)


@pytest.mark.parametrize('budget',[1,2,40,180])
def test_history_budget_holds_after_long_message_and_many_turns(budget):
    history=ConversationHistory(max_characters=budget)
    for _ in range(100):
        history.add('user','x'*1000)
        assert history.total_characters() <= budget
    assert all(m['role']!='developer' for m in history.as_messages())


def test_versions_survive_reconstruction_and_duplicate_update(tmp_path):
    path=tmp_path/'facts.json'
    old=candidate(); new=candidate('Go',source_id='s2')
    sources={c.source_id:c.source_text for c in [old,new]}
    store=FactStore(path)
    assert store.apply('u',old,sources=sources)['event']=='inserted'
    assert store.apply('u',new,sources=sources)['event']=='superseded'
    reloaded=FactStore(path)
    assert [(f.value,f.status) for f in reloaded.records]==[('Python','superseded'),('Go','active')]
    assert reloaded.records[1].supersedes==reloaded.records[0].id
    assert reloaded.active('other')==[]
    assert reloaded.apply('u',new,sources=sources)['event']=='duplicate'
    assert len(FactStore(path).records)==2


def test_low_confidence_cannot_supersede_active_fact(tmp_path):
    store=FactStore(tmp_path/'facts.json')
    good=candidate(); bad=candidate('Rust',source_id='s2',confidence=.01)
    sources={c.source_id:c.source_text for c in [good,bad]}
    store.apply('u',good,sources=sources)
    before=store.path.read_bytes()
    assert store.apply('u',bad,sources=sources)['event']=='needs_review'
    assert store.path.read_bytes()==before
    assert store.active('u')[0].value=='Python'


@pytest.mark.parametrize('sources',[{}, {'s1':'wrong text'}, {'other':'I prefer Python.'}])
def test_invalid_provenance_is_rejected(sources):
    with pytest.raises(ValueError):
        validate_extraction(MemoryExtraction(candidates=[candidate()]),sources)


def test_duplicate_source_ids_are_rejected():
    c=candidate()
    with pytest.raises(ValueError):
        validate_extraction(MemoryExtraction(candidates=[c,c]),{'s1':c.source_text})


def test_project_value_does_not_change_category():
    project=candidate('Go',category='current_project',key='current_project')
    assert canonicalize(project).key=='current_project'


def test_drop_cannot_carry_profile_fields():
    with pytest.raises(ValueError): candidate(decision='drop')


@pytest.mark.parametrize('text',['Remember 4242 4242 4242 4242.', 'Email demo@example.com.'])
def test_guard_blocks_before_runner_is_called(text):
    calls=[]
    async def spy(*args,**kwargs): calls.append(args)
    with pytest.raises(ValueError): asyncio.run(guarded_run(spy,None,text))
    assert calls==[]


def test_guard_forwards_allowed_input():
    async def spy(agent,text,**kwargs): return (text,kwargs)
    assert asyncio.run(guarded_run(spy,None,'I prefer Go.',max_turns=2))==('I prefer Go.',{'max_turns':2})
