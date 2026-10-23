"""Símplex primal de dos fases, pivotes explícitos y regla de Bland."""
from copy import deepcopy
from math import isfinite
from .phase_one import preparar

EPS = 1e-9

def resolver(modelo, *, max_iteraciones=1000):
    p = preparar(modelo)
    cols, filas, base, ids = (deepcopy(p[k]) for k in ('columnas','filas','base','filas_ids'))
    tablas, pivotes = [], []
    fase, obj = 1, []

    def objetivo(costes):
        o = [-v for v in costes] + [0.]
        for b, f in zip(base, filas):
            o = [x + costes[b]*y for x,y in zip(o,f)]
        return o

    def registrar(operaciones=None, pivote=None):
        tablas.append(dict(numero=len(tablas), fase=fase, columnas=cols+['RHS'],
            filas_ids=['OBJ']+ids[:], base=[cols[b] for b in base],
            valores=deepcopy([obj]+filas), operaciones=operaciones or [], pivote=pivote))

    def pivotar(r, c, razones):
        nonlocal obj
        valor = filas[r][c]
        salida = cols[base[r]]
        filas[r] = [v/valor for v in filas[r]]
        ops = [f'{ids[r]} ← {ids[r]} / {valor:.10g}']
        for j in range(len(filas)):
            if j == r: continue
            factor = filas[j][c]
            filas[j] = [x-factor*y for x,y in zip(filas[j],filas[r])]
            ops.append(f'{ids[j]} ← {ids[j]} - ({factor:.10g}) × {ids[r]}')
        factor = obj[c]
        obj = [x-factor*y for x,y in zip(obj,filas[r])]
        ops.append(f'OBJ ← OBJ - ({factor:.10g}) × {ids[r]}')
        base[r] = c
        pivote = dict(fila=ids[r], columna=cols[c], valor=valor, saliente=salida, razones=razones,
                      tabla_antes=len(tablas)-1, fase=fase)
        pivotes.append(pivote)
        registrar(ops, pivote)

    def ejecutar():
        while True:
            if not all(isfinite(x) for f in [obj]+filas for x in f): return 'numerical_error'
            entrantes = [j for j,v in enumerate(obj[:-1]) if v < -EPS and j not in base]
            if not entrantes: return 'optimal'
            if len(pivotes) >= max_iteraciones: return 'iteration_limit'
            c = min(entrantes)
            razones = {ids[i]: max(0.,f[-1])/f[c] if f[c] > EPS else None for i,f in enumerate(filas)}
            validas = [i for i in range(len(filas)) if razones[ids[i]] is not None]
            if not validas: return 'unbounded'
            minimo = min(razones[ids[i]] for i in validas)
            r = min((i for i in validas if abs(razones[ids[i]]-minimo) <= EPS), key=lambda i:base[i])
            pivotar(r,c,razones)

    estado = 'optimal'
    if p['artificiales']:
        obj = objetivo(p['objetivo_fase1'])
        registrar(['Fase I: maximizar U = -W; W es la suma de artificiales.'])
        estado = ejecutar()
        if estado == 'optimal' and obj[-1] < -EPS: estado = 'infeasible'
        if estado == 'optimal':
            for r in range(len(filas)-1,-1,-1):
                if base[r] not in p['artificiales']: continue
                c = next((j for j in range(len(cols)) if j not in p['artificiales'] and j not in base and abs(filas[r][j]) > EPS),None)
                if c is not None:
                    if len(pivotes) >= max_iteraciones:
                        estado = 'iteration_limit'; break
                    pivotar(r,c,{})
                else:
                    filas.pop(r); base.pop(r); ids.pop(r)
            if estado == 'optimal':
                conservar = [j for j in range(len(cols)) if j not in p['artificiales']]
                filas = [[f[j] for j in conservar]+[f[-1]] for f in filas]
                base = [conservar.index(b) for b in base]
                cols = [cols[j] for j in conservar]
    if estado == 'optimal':
        fase = 2
        factor = 1 if modelo['sentido']=='max' else -1
        obj = objetivo([factor*x for x in modelo['objetivo']]+[0.]*(len(cols)-len(modelo['objetivo'])))
        registrar(['Fase II: objetivo original; para MIN se maximiza Y=-Z.'])
        estado = ejecutar()
    valores = [0.]*len(modelo['objetivo'])
    if estado == 'optimal':
        for b,f in zip(base,filas):
            if b < len(valores): valores[b] = f[-1]
    comprobacion = []
    if estado == 'optimal':
        for i,r in enumerate(modelo['restricciones'],1):
            lhs = sum(x*y for x,y in zip(r['coeficientes'],valores))
            delta = lhs-r['rhs']; tol=1e-7*(1+abs(lhs)+abs(r['rhs']))
            cumple = delta<=tol if r['signo']=='<=' else delta>=-tol if r['signo']=='>=' else abs(delta)<=tol
            comprobacion.append(dict(fila=f'R{i}',lhs=lhs,rhs=r['rhs'],signo=r['signo'],cumple=cumple,holgura=abs(delta)))
        if not all(r['cumple'] for r in comprobacion) or min(valores)<-1e-7: estado='numerical_error'
    return dict(estado=estado,fase=fase,variables=dict(zip('abcdef',valores)) if estado=='optimal' else {},
        objetivo=sum(x*y for x,y in zip(modelo['objetivo'],valores)) if estado=='optimal' else None,
        preparacion=p,tabla_inicial=tablas[0],tablas=tablas,pivotes=pivotes,comprobacion=comprobacion)
