import json
from types import SimpleNamespace
import pytest
from src.config import Settings
from src.harness.loop import AgentHarness
from src.tools import DEFAULT_TOOLS, ToolRegistry


def response(name=None, arguments=None, text='', status='completed'):
    calls = [] if name is None else [SimpleNamespace(type='function_call', name=name,
        arguments=arguments, call_id='c1')]
    return SimpleNamespace(id='test', output=calls, output_text=text, status=status)


class FakeClient:
    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.inputs = []
        self.responses = SimpleNamespace(create=self.create)
    def create(self, **kwargs):
        self.inputs.append(list(kwargs['input']))
        return next(self.outputs)


def harness(outputs):
    client = FakeClient(outputs)
    return AgentHarness(settings=Settings(provider='mock'), client=client), client


def test_dependent_calls_are_returned_to_model():
    h, client = harness([response('search_notes', '{"query":"memory"}'),
        response('calculate', '{"expression":"2+3"}'), response(text='5')])
    result = h.run('read and calculate', max_steps=3)
    assert result.status == 'completed'
    assert result.answer == '5'
    assert [e['metadata']['tool'] for e in result.trace if e['kind'] == 'tool'] == ['search_notes','calculate']
    observations = [i for i in client.inputs[-1] if isinstance(i,dict) and i.get('type') == 'function_call_output']
    assert len(observations) == 2
    assert json.loads(observations[-1]['output'])['result'] == 5


@pytest.mark.parametrize('name,args', [('unknown','{}'), ('calculate','not-json'),
    ('calculate','[]'), ('calculate','{"expression":3}'), ('calculate','{"expression":"1/0"}')])
def test_tool_failures_return_observations_and_can_recover(name, args):
    h, client = harness([response(name,args),response(text='Handled the failed request.')])
    result = h.run('task',max_steps=2)
    assert result.status == 'completed'
    assert any(e['kind']=='error' for e in result.trace)
    assert any(i.get('type')=='function_call_output' and 'error' in i['output']
               for i in client.inputs[1] if isinstance(i,dict))


@pytest.mark.parametrize('output,expected', [(response(status='incomplete'),'incomplete'),
    (response(text=''),'empty_output')])
def test_non_answers_do_not_become_success(output,expected):
    h,_=harness([output])
    result=h.run('task')
    assert result.status==expected
    assert result.trace[-1]['kind']=='error'


def test_limit_counts_model_requests():
    h,client=harness([response('calculate','{"expression":"2+3"}')])
    assert h.run('task',max_steps=1).status=='max_steps'
    assert len(client.inputs)==1


@pytest.mark.parametrize('provider,limit',[('mock',0),('openai',0),('typo',4)])
def test_invalid_configuration_is_rejected(provider,limit):
    with pytest.raises(ValueError):
        AgentHarness(settings=Settings(provider=provider)).run('task',max_steps=limit)


def test_custom_registry_mock_does_not_assume_search_tool():
    h=AgentHarness(ToolRegistry([DEFAULT_TOOLS[1]]),Settings(provider='mock'))
    assert h.run('task').status=='completed'


def test_model_transport_failure_is_explicit():
    h,_=harness([])
    assert h.run('task').status=='model_error'
