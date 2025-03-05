from akl.workflow import State, Step

async def test_workflow_simple():
    class Val(State):
        val: int = 0

    class Add(Step):
        x: int = 1

        async def work(self, input: Val) -> Val:
            input.val += self.x
            return input

    class Mul(Step):
        by: int = 2

        async def work(self, input: Val) -> Val:
            input.val *= self.by
            return input

    s = Val(val=0)
    p = Add(x=1) | Mul(by=2) | Add(x=1) | Mul(by=2)

    expected = Val(val=6)
    actual = await p.eval(s)
    assert actual.val == expected.val
