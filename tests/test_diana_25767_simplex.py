import random
import pytest
from scipy.optimize import linprog
from backend.simplex.simplex import resolver
from .casos import modelo,MAX,MIN

@pytest.mark.parametrize('m,estado,z',[
 (MAX,'optimal',13),(MIN,'optimal',8),
 (modelo([1,1],[([1,1],'<=',2),([1,1],'>=',5)]),'infeasible',None),
 (modelo([1,1],[([1,-1],'<=',2)]),'unbounded',None),
 (modelo([1,2],[([1,1],'=',4)]),'optimal',8),
 (modelo([1,1],[([-1,-1],'>=',-3)]),'optimal',3),
 (modelo([0,0],[([0,0],'=',0)]),'optimal',0),
 (modelo([1,1],[([0,0],'=',1)]),'infeasible',None),
 (modelo([.5,1.2],[([1,0],'<=',2),([0,1],'<=',3)]),'optimal',4.6),
 (modelo([1,1],[([1,1],'=',3),([2,2],'=',6)]),'optimal',3),
 (modelo([1]*6,[([int(i==j) for j in range(6)],'<=',1) for i in range(6)]),'optimal',6),
 (modelo([7,2],[([1,1],'<=',9),([1,0],'<=',4)]),'optimal',38),
 (modelo([1,1],[([1,0],'>=',2),([0,1],'>=',3)],'min'),'optimal',5),
 (modelo([10,-57,-9,-24],[([.5,-5.5,-2.5,9],'<=',0),([.5,-1.5,-.5,1],'<=',0),([1,0,0,0],'<=',1)]),'optimal',1)
])
def test_casos(m,estado,z):
    r=resolver(m);assert r['estado']==estado
    if z is not None:
        assert r['objetivo']==pytest.approx(z)
        assert all(c['cumple'] for c in r['comprobacion'])
    for t in r['tablas']:
        assert t['filas_ids'][0]=='OBJ'
        assert all(len(f)==len(t['columnas']) for f in t['valores'])

def test_pivote_y_operaciones():
    r=resolver(MAX)
    assert r['variables']==pytest.approx(dict(a=2,b=0,c=1))
    for t in r['tablas']:
        if not t['pivote']: continue
        p=t['pivote'];j=t['columnas'].index(p['columna']);i=t['filas_ids'].index(p['fila'])
        assert [f[j] for f in t['valores']]==pytest.approx([int(k==i) for k in range(len(t['valores']))])
        assert t['operaciones']

def test_modelos_nuevos_con_oraculo():
    rng=random.Random(9365)
    for _ in range(100):
        n=rng.randint(2,6);x=[rng.uniform(.2,3) for _ in range(n)]
        rs=[([int(i==j) for j in range(n)],'<=',x[i]+3) for i in range(n)]
        for k in range(5):
            a=[rng.randint(-3,5) for _ in range(n)];s=rng.choice(['<=','>=','=']);b=sum(u*v for u,v in zip(a,x))+(rng.random() if s=='<=' else -rng.random() if s=='>=' else 0)
            rs.append((a,s,b))
        c=[rng.uniform(-3,5) for _ in range(n)];sense=rng.choice(['max','min']);m=modelo(c,rs,sense)
        aub=[];bub=[];aeq=[];beq=[]
        for a,s,b in rs:
            if s=='=': aeq.append(a);beq.append(b)
            else:
                f=1 if s=='<=' else -1;aub.append([f*v for v in a]);bub.append(f*b)
        oracle=linprog([(-1 if sense=='max' else 1)*v for v in c],A_ub=aub,b_ub=bub,A_eq=aeq or None,b_eq=beq or None,method='highs')
        r=resolver(m);assert oracle.success;assert r['estado']=='optimal';assert r['objetivo']==pytest.approx(oracle.fun*(-1 if sense=='max' else 1),abs=1e-6)


def test_limite_no_es_optimo():
    r=resolver(MAX,max_iteraciones=0)
    assert r['estado']=='iteration_limit' and r['objetivo'] is None
