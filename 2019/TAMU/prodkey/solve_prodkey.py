#!/usr/bin/env python
# coding: utf-8
import angr
import claripy
import time

def main(n):
    # Load the binary.
    p = angr.Project('./keygenme')

    # Last byte should be a newline.
    flag_chars = [claripy.BVS('flag_%d' % i, 8) for i in range(n)]
    flag = claripy.Concat(*flag_chars + [claripy.BVV(b'\n')])

    # Construct the initial program state for analysis.
    st = p.factory.full_init_state(
            args=['./keygenme'],
            add_options=angr.options.unicorn,
            stdin=flag,
            remove_options={angr.sim_options.ALL_FILES_EXIST}
    )

    # Constrain the first 29 bytes to be reasonable ASCII chars:
    for k in flag_chars:
        st.solver.add(k != 0)
        st.solver.add(k != 10)

    # Construct a SimulationManager to perform symbolic execution.
    # Step until there is nothing left to be stepped.
    sm = p.factory.simulation_manager(st)
    sm.run()

    # Get the stdout of every path that reached an exit syscall.
    # If we reach state where the following is printed, then we got a winning input:
    # "Too bad the flag is only on the remote server!"
    for pp in sm.deadended:
        if b'flag' in pp.posix.dumps(1):
            return pp.posix.dumps(0)
    return "fail"

if __name__ == "__main__":
    before = time.time()

    for i in range(11, 64)[::-1]:
        res = main(i)
        print('[{}]: {}'.format(i, res))
        if res != 'fail':
            break

    after = time.time()
    print("Time elapsed: {}".format(after - before))
