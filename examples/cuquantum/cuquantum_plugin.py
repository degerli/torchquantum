from cuquantum import contract
from cuquantum import CircuitToEinsum
import torchquantum as tq
from torchquantum.plugins import op_history2qiskit
from torchquantum.measurement import expval_joint_analytical
import cupy as cp

def expval_joint_analytical_cuquantum(qdev, observable):
    """Computes the expectation value of a joint observable using cuquantum.

    Args:
        qdev (QuantumDevice): Quantum device to compute the expectation value on.
        observable (str): Joint observable to compute the expectation value of.

    Returns:
        float: The expectation value of the joint observable.
    """
    op_history = qdev.op_history
    qiskit_circ = op_history2qiskit(qdev.n_wires, op_history)
    myconverter = CircuitToEinsum(qiskit_circ, dtype='complex128', backend=cp)
    expression, operands = myconverter.expectation(observable, lightcone=True)
    expec = contract(expression, *operands)
    return expec


if __name__ == '__main__':
    
    ops = [
        {'name': 'u3', 'wires': 0, 'trainable': True},
        {'name': 'u3', 'wires': 1, 'trainable': True},
        {'name': 'cx', 'wires': [0, 1]},
        {'name': 'cx', 'wires': [1, 0]},
        {'name': 'u3', 'wires': 0, 'trainable': True},
        {'name': 'u3', 'wires': 1, 'trainable': True},
        {'name': 'cx', 'wires': [0, 1]},
        {'name': 'cx', 'wires': [1, 0]},
    ]

    qmodule = tq.QuantumModule.from_op_history(ops)

    qdev = tq.QuantumDevice(n_wires=2, bsz=1, record_op=True)

    qmodule(qdev)

    op_history = qdev.op_history

    # print(op_history)

    qiskit_circ = op_history2qiskit(qdev.n_wires, op_history)
    # print(qiskit_circ)

    myconverter = CircuitToEinsum(qiskit_circ, dtype='complex128', backend=cp)
    pauli_string = 'IX'
    expression, operands = myconverter.expectation(pauli_string, lightcone=True)
    expec = contract(expression, *operands)
    print(f'expectation value for {pauli_string}: {expec}')

    print(f"torchquantum expval: {expval_joint_analytical(qdev, pauli_string)}")
    print(expval_joint_analytical_cuquantum(qdev, pauli_string))
    

    # # expectation value from reduced density matrix
    # qubits = myconverter.qubits
    # where = qubits[1:5]
    # rdm_expression, rdm_operands = myconverter.reduced_density_matrix(where, lightcone=True)
    # rdm = contract(rdm_expression, *rdm_operands)

    # pauli_x = cp.asarray([[0,1],[1,0]], dtype=myconverter.dtype)
    # pauli_z = cp.asarray([[1,0],[0,-1]], dtype=myconverter.dtype)
    # expec_from_rdm = cp.einsum('abcdABCD,aA,bB,cC,dD->', rdm, pauli_x, pauli_x, pauli_z, pauli_z)


    # print(f"is expectation value in agreement?", cp.allclose(expec, expec_from_rdm))

