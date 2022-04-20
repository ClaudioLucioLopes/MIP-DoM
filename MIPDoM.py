import numpy as np
import gurobipy as gp
from gurobipy import GRB


def DOM_distance(A, B):
    # A = [1.5, 1, 2]
    # B = [1.5, 1.2, 1.9]
    dist = 0
    for i in range(len(A)):
        if (A[i] > B[i]):
            dist += (A[i] - B[i])
    return dist


def DOM_distance_point_set(A, B):
    # A = [1.5, 1, 2]
    # B = [1.5, 1.2, 1.9]
    B_min = np.min(B, axis=0)
    return DOM_distance(A, B_min)


# eliminate some points already dominated in P and Q
def adjust_P_Q(P, Q):
    nobj = P.shape[1]
    # print('Q is dominated by P:')
    q_dominated_by_p = []
    for q_i, q in enumerate(Q):
        if np.sum(np.sum(np.greater_equal(q, P), axis=1) == nobj) > 0:
            # print(q_i, q)'
            q_dominated_by_p.append(q_i)
    # print('Q is dominated by someone other member o q:')
    q_dominated_by_q = []
    for q_i, q in enumerate(Q):
        if np.sum(np.sum(np.greater(q, Q), axis=1) == nobj) > 0:
            # print(q_i, q)
            q_dominated_by_q.append(q_i)
    # print('P is dominated by someone other member o p:')
    p_dominated_by_p = []
    for p_i, p in enumerate(P):
        if np.sum(np.sum(np.greater(p, P), axis=1) == nobj) > 0:
            # print(p_i, p)
            p_dominated_by_p.append(p_i)
    Q = np.delete(Q, np.hstack([q_dominated_by_p, q_dominated_by_q]).tolist(), axis=0)
    P = np.delete(P, p_dominated_by_p, axis=0)
    return P, Q

###################################################################################################
#Input: P set, Q set, logprint(True or false) if the log should be presented, model_name with the path to save the LP model
#Output: MIP-DoM value, and the P' generated by the method(dictionary with the p index  as key and the coordinates for the P')
###################################################################################################
def get_min_dom_mip_gurobi(P, Q, logprint=False, gapperc=1e-04, model_name='teste'):
    model = gp.Model("get_min_dom_mip_gurobi")

    P1, Q1 = adjust_P_Q(P, Q)
    if Q1.shape[0] != 0:
        Q = Q1
    if P1.shape[0] != 0:
        P = P1

    num_P = P.shape[0]
    num_Q = Q.shape[0]
    num_J = P.shape[1]

    min_obj_Q = np.min(Q, axis=0)

    lb_P = np.zeros(shape=(num_P, num_J))
    ub_P = np.zeros(shape=(num_P, num_J))
    for p in range(num_P):
        for j in range(num_J):
            lb_P[p][j] = np.min([P[p][j], min_obj_Q[j]])
            ub_P[p][j] = P[p][j]

    idx = [(p, q, j) for j in range(num_J) for q in range(num_Q) for p in range(num_P)]
    ZPQO = model.addVars(idx, vtype=GRB.CONTINUOUS,name='ZPQO')
    

    idx = [(p, q, j,d ) for d in range(2) for j in range(num_J) for q in range(num_Q) for p in range(num_P)]
    d_ZPQO = model.addVars(idx,vtype=GRB.BINARY,name='d_ZPQO')

    idx = [(p, q) for q in range(num_Q) for p in range(num_P)]
    XPQ = model.addVars(idx, vtype=GRB.BINARY, name="XPQ")

    idx = [(p) for p in range(num_P)]
    XP = model.addVars(idx, vtype=GRB.BINARY, name="XP")

    idx = [(p, j) for j in range(num_J) for p in range(num_P)]
    ZPO = model.addVars(idx, vtype=GRB.CONTINUOUS, name="ZPO")
    plPO = model.addVars(idx, vtype=GRB.CONTINUOUS, name="plPO", ub=np.reshape(ub_P, ub_P.shape[0] *ub_P.shape[1],order='F'),lb=np.reshape(lb_P, lb_P.shape[0] *lb_P.shape[1],order='F'))


    # objective function
    obj_ZPO = gp.quicksum(ZPO[p, j] for p in range(num_P) for j in range(num_J))
    obj_ZPQO = gp.quicksum(ZPQO[p, q, j] for j in range(num_J) for p in range(num_P) for q in range(num_Q))
    model.setObjective(obj_ZPO + obj_ZPQO, GRB.MINIMIZE)

    # Zp must be greather than Zpq
    model.addConstr(gp.quicksum(ZPO[p, j] for p in range(num_P) for j in range(num_J)) >= gp.quicksum(
        ZPQO[p, q, j] for p in range(num_P) for q in range(num_Q) for j in range(num_J)))

    # constraints
    # for each Q must have be just one P dominating
    for q in range(num_Q):
        model.addConstr(gp.quicksum(XPQ[p, q] for p in range(num_P)) == 1)

    model.addConstr(gp.quicksum(XPQ[p, q] for p in range(num_P) for q in range(num_Q)) == num_Q)

    # if P will be selected than XP[p] = 1
    for p in range(num_P):
        for q in range(num_Q):
            model.addConstr(XP[p] >= XPQ[p, q])
        model.addConstr(XP[p] <= gp.quicksum(XPQ[p, q] for q in range(num_Q)))

    for p in range(num_P):
        for j in range(num_J):
            model.addConstr(ZPO[p, j] >= 0)
            model.addConstr(ZPO[p, j] >= (P[p][j] * XP[p] - plPO[p, j]))
            model.addConstr(ZPO[p, j] <= P[p][j] * XP[p])


    for p in range(num_P):
        for q in range(num_Q):
            for j in range(num_J):
                model.addConstr(ZPQO[p, q, j] >= 0)
                model.addConstr(ZPQO[p, q, j] >= plPO[p, j] - Q[q][j] - P[p][j] * (1 - XPQ[p, q]))
                u_max = max(0, ub_P[p][j] - Q[q][j])
                model.addConstr(ZPQO[p, q, j] <= 0 + (u_max - 0) * (1 - d_ZPQO[p, q, j,0]))
                model.addConstr(
                    ZPQO[p, q, j] <= plPO[p, j] - Q[q][j] + (u_max - (lb_P[p][j] - Q[q][j])) * (1 - d_ZPQO[p, q, j,1]))
                model.addConstr(gp.quicksum(d_ZPQO[p, q, j, d] for d in range(2)) == 1)


    model.setParam('MIPFocus', 3)
    model.setParam('MIPGap', gapperc)


    model.optimize()
    #model.computeIIS()
    #model.write("/home/claudiolucio/Documents/GDrive/Proposta doc/experimentos/GUROBI/model.ilp")
    model.printStats()
    model.printQuality()

    #Auxiliary variables
    p_pl = model.getAttr('x', plPO)
    zpj = model.getAttr('x', ZPO)

    zpqj = model.getAttr('x', ZPQO)

    xpq = model.getAttr('x', XPQ)
    xp = model.getAttr('x', XP)

    p_line_ret = {}
    p_index_ret = []
    if model.status == GRB.OPTIMAL:
        p_pl = model.getAttr('x', plPO)
        zpj = model.getAttr('x', ZPO)

        zpqj = model.getAttr('x', ZPQO)

        xpq = model.getAttr('x', XPQ)
        xp = model.getAttr('x', XP)
        if logprint:
            print('Total distance = ', model.getObjective().getValue())
        for p in range(num_P):
            print_p = True
            if zpj.sum(p, '*').getValue() > 0:
                if p not in p_index_ret:
                    p_index_ret.append(p)
                print('Improvement on P%d , total of %5.5f:' % (p + 1, zpj.sum(p, '*').getValue()),
                      [p_pl.select(p, ij) for ij in range(num_J)] )
                p_line_ret[p] = np.array([p_pl.select(p, ij) for ij in range(num_J)]).reshape(-1,num_J)[0]
            for q in range(num_Q):
                dominance_movement = 0
                if (zpj.sum(p, '*').getValue() > 0):
                    if print_p:
                        print_p = False
                if xpq.select(p, q)[0] > 0:
                    dominance_movement += zpqj.sum(p, q, '*').getValue()
                    if logprint:
                        print('P%d  dominates Q%d, distance of %5.5f:' % (p + 1, q + 1, dominance_movement))
                    if dominance_movement > 0.00000000000000001:
                        if print_p:
                           p_line_ret[ p ] =P[p]
                        for ij in range(num_J):
                            if zpqj.sum(p, q, ij).getValue() > 0:
                                p_line_ret[ p ][ij] =p_line_ret[p][ij]-zpqj.sum(p, q, ij).getValue()

                        p_index_ret.append(p)
                        print([(ij,zpqj.sum(p, q, ij).getValue()) for ij in range(num_J) if zpqj.sum(p, q, ij).getValue() > 0])
    return model.getObjective().getValue(),p_line_ret