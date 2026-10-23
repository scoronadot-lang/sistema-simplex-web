import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ActionIcon, Alert, AppShell, Badge, Box, Burger, Button, Card, Divider,
  Group, Modal, NumberInput, PasswordInput, Select, SegmentedControl, SimpleGrid, Stack,
  Table, Text, TextInput, Title, Tooltip,
} from '@mantine/core';
import {
  IconActivity, IconArrowLeft, IconArrowRight, IconBrain, IconCheck,
  IconCirclePlus, IconClipboardList, IconDatabase, IconDeviceFloppy,
  IconExternalLink, IconFilePlus, IconHistory, IconMathFunction,
  IconMinus, IconPlayerPlay, IconRefresh, IconSearch, IconSettings,
  IconTrash, IconUpload,
} from '@tabler/icons-react';
import { api } from '../../js/kevin_9365_api.js';

const letters = 'abcdef';
const navItems = [
  { id: 'modelo', label: 'Modelo', icon: IconMathFunction },
  { id: 'preparacion', label: 'Preparación', icon: IconSettings },
  { id: 'procedimiento', label: 'Procedimiento', icon: IconActivity },
  { id: 'resultado', label: 'Resultado', icon: IconCheck },
  { id: 'historial', label: 'Historial', icon: IconHistory },
];
const statusLabels = {
  optimal: 'Óptimo', infeasible: 'Infactible', unbounded: 'No acotado',
  iteration_limit: 'Límite de iteraciones', numerical_error: 'Error numérico', pending: 'Pendiente',
};
const statusDescriptions = {
  optimal: 'Se encontró una solución óptima y se verificaron las restricciones.',
  infeasible: 'No existe una solución que satisfaga todas las restricciones.',
  unbounded: 'El objetivo puede mejorar sin límite dentro de la región factible.',
  iteration_limit: 'El motor alcanzó el límite de iteraciones configurado.',
  numerical_error: 'El motor detectó una inconsistencia numérica; no se muestra un óptimo.',
};

const blankModel = (n = 3) => ({
  nombre: '', sentido: 'max', objetivo: Array(n).fill(''),
  restricciones: [{ coeficientes: Array(n).fill(''), signo: '<=', rhs: '' }],
});
const demoModel = {
  nombre: 'Ejemplo · maximización', sentido: 'max', objetivo: ['5', '4', '3'],
  restricciones: [
    { coeficientes: ['2', '3', '1'], signo: '<=', rhs: '5' },
    { coeficientes: ['4', '1', '2'], signo: '<=', rhs: '11' },
    { coeficientes: ['3', '4', '2'], signo: '<=', rhs: '8' },
  ],
};

function numeric(value) {
  if (value === '' || value === null || value === undefined) return null;
  const parsed = Number(String(value).trim().replace(',', '.'));
  return Number.isFinite(parsed) ? parsed : null;
}
function numberText(value, digits = 4) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) return '—';
  return new Intl.NumberFormat('es-GT', { maximumFractionDigits: digits }).format(Number(value));
}
function readModel(draft) {
  return {
    nombre: draft.nombre.trim() || 'Sin título', sentido: draft.sentido,
    objetivo: draft.objetivo.map(numeric),
    restricciones: draft.restricciones.map(row => ({
      coeficientes: row.coeficientes.map(numeric), signo: row.signo, rhs: numeric(row.rhs),
    })),
  };
}
function validate(draft) {
  const errors = [];
  if (!draft.nombre.trim()) errors.push('Escribe un nombre para el modelo.');
  draft.objetivo.forEach((value, index) => {
    if (numeric(value) === null) errors.push(`Completa un coeficiente válido para ${letters[index]}.`);
  });
  draft.restricciones.forEach((row, r) => {
    row.coeficientes.forEach((value, c) => {
      if (numeric(value) === null) errors.push(`Completa ${letters[c]} en la restricción ${r + 1}.`);
    });
    if (numeric(row.rhs) === null) errors.push(`Completa el lado derecho de la restricción ${r + 1}.`);
  });
  if (draft.restricciones.length < 1) errors.push('Agrega al menos una restricción.');
  if (draft.restricciones.length > 40) errors.push('El máximo permitido es 40 restricciones.');
  return errors;
}
function hydrateModel(model) {
  const n = model?.objetivo?.length || 3;
  return {
    nombre: model?.nombre || '', sentido: model?.sentido || 'max',
    objetivo: Array.from({ length: n }, (_, i) => model?.objetivo?.[i] ?? ''),
    restricciones: (model?.restricciones?.length ? model.restricciones : [{ }]).map(row => ({
      coeficientes: Array.from({ length: n }, (_, i) => row.coeficientes?.[i] ?? ''),
      signo: row.signo || '<=', rhs: row.rhs ?? '',
    })),
  };
}
function prettyEquation(coefficients, names, relation, rhs) {
  const terms = coefficients.flatMap((coefficient, i) => {
    if (Math.abs(Number(coefficient)) < 1e-10) return [];
    const sign = coefficient < 0 ? ' − ' : ' + ';
    return [`${sign}${numberText(Math.abs(coefficient), 6)} ${names[i]}`];
  });
  const left = terms.length ? terms.join('').replace(/^ \+ /, '') : '0';
  return `${left} ${relation} ${numberText(rhs, 6)}`;
}

function Tableau({ table, highlight = null }) {
  if (!table?.valores?.length) return <Alert color="gray">No hay una tabla disponible.</Alert>;
  const columns = table.columnas || [];
  return (
    <Table.ScrollContainer minWidth={Math.max(620, 100 + columns.length * 82)} type="native">
      <Table className="tableau" withTableBorder withColumnBorders highlightOnHover>
        <Table.Thead><Table.Tr><Table.Th>Base</Table.Th>{columns.map((name, i) => <Table.Th key={`${name}-${i}`}>{name}</Table.Th>)}</Table.Tr></Table.Thead>
        <Table.Tbody>
          {table.valores.map((row, r) => {
            const label = r === 0 ? 'OBJ' : table.base?.[r - 1] || table.filas_ids?.[r] || `R${r}`;
            return <Table.Tr key={`${r}-${label}`} className={r === 0 ? 'objective-row' : ''}>
              <Table.Th>{label}</Table.Th>
              {row.map((value, c) => {
                const pivotCell = highlight?.row === r && highlight?.column === c;
                return <Table.Td key={c} className={`${c === columns.length - 1 ? 'rhs-cell' : ''} ${pivotCell ? 'pivot-cell' : ''}`}>
                  {numberText(value, 6)}
                </Table.Td>;
              })}
            </Table.Tr>;
          })}
        </Table.Tbody>
      </Table>
    </Table.ScrollContainer>
  );
}

function ModelCard({ model }) {
  const vars = letters.slice(0, model.objetivo.length).split('');
  const objective = model.objetivo.map((value, i) => `${i ? (value < 0 ? ' − ' : ' + ') : value < 0 ? '−' : ''}${numberText(Math.abs(value), 6)}${vars[i]}`).join('');
  return <Card className="surface-card" withBorder>
    <Group justify="space-between" mb="sm"><Text fw={700}>Modelo original</Text><Badge variant="light" color="cyan">{model.sentido === 'max' ? 'Maximizar' : 'Minimizar'}</Badge></Group>
    <Text className="equation">{model.nombre}: {model.sentido === 'max' ? 'Max' : 'Min'} Z = {objective}</Text>
    <Stack gap={5} mt="sm">{model.restricciones.map((row, i) => <Text key={i} className="equation muted-text">R{i + 1}: {prettyEquation(row.coeficientes, vars, row.signo, row.rhs)}</Text>)}
      <Text className="equation muted-text">{vars.join(', ')} ≥ 0</Text>
    </Stack>
  </Card>;
}

function ModelEditor({ draft, setDraft, onSolve, busy, errors, onDemo, onClear }) {
  const n = draft.objetivo.length;
  const vars = letters.slice(0, n).split('');
  const update = (fn) => setDraft(current => fn(current));
  const changeVarCount = value => update(current => {
    const size = Number(value);
    return { ...current, objetivo: Array.from({ length: size }, (_, i) => current.objetivo[i] ?? ''),
      restricciones: current.restricciones.map(row => ({ ...row, coeficientes: Array.from({ length: size }, (_, i) => row.coeficientes[i] ?? '') })) };
  });
  return <fieldset className="form-fieldset" disabled={busy}><Stack gap="lg">
    <Group justify="space-between" align="end" wrap="wrap">
      <div><Badge color="cyan" variant="light" leftSection={<IconBrain size={14} />}>CAPTURA DEL MODELO</Badge><Title order={2} mt="xs">Define tu problema</Title><Text c="dimmed" mt={4}>Completa los datos. El motor calculará preparación, procedimiento y estado usando tu modelo.</Text></div>
      <Group><Button variant="default" leftSection={<IconUpload size={16} />} onClick={onDemo}>Cargar ejemplo</Button><Button variant="subtle" leftSection={<IconFilePlus size={16} />} onClick={onClear}>Nuevo en blanco</Button></Group>
    </Group>
    {errors.length > 0 && <Alert color="red" title="Revisa estos campos">{errors.slice(0, 5).map((error, i) => <Text key={i} size="sm">• {error}</Text>)}{errors.length > 5 && <Text size="sm">y {errors.length - 5} campos más.</Text>}</Alert>}
    <Card className="surface-card" withBorder>
      <Group align="end" grow wrap="wrap">
        <TextInput label="Nombre del modelo" placeholder="Ej. Plan de producción" value={draft.nombre} maxLength={120} error={errors.some(item => item.includes('nombre')) ? 'Escribe un nombre.' : null} onChange={event => update(m => ({ ...m, nombre: event.currentTarget.value }))} />
        <Select label="Variables de decisión" value={String(n)} data={Array.from({ length: 5 }, (_, i) => ({ value: String(i + 2), label: `${i + 2} variables (${letters.slice(0, i + 2).split('').join(', ')})` }))} onChange={changeVarCount} allowDeselect={false} />
      </Group>
      <Divider my="lg" label="Función objetivo" labelPosition="left" />
      <SegmentedControl value={draft.sentido} onChange={value => update(m => ({ ...m, sentido: value }))} data={[{ value: 'max', label: 'Maximizar' }, { value: 'min', label: 'Minimizar' }]} mb="md" />
      <Group align="end" wrap="wrap" className="coefficient-row">
        <Text className="formula-prefix">{draft.sentido === 'max' ? 'Max Z =' : 'Min Z ='}</Text>
        {vars.map((name, i) => <NumberInput key={name} label={`Coeficiente de ${name}`} aria-label={`Coeficiente de ${name} en función objetivo`} value={draft.objetivo[i]} error={errors.some(item => item.includes(`para ${name}`)) ? 'Requerido' : null} onChange={value => update(m => ({ ...m, objetivo: m.objetivo.map((item, j) => j === i ? String(value) : item) }))} allowNegative hideControls decimalSeparator="." />)}
      </Group>
    </Card>
    <Card className="surface-card" withBorder>
      <Group justify="space-between" mb="md"><div><Text fw={700}>Restricciones</Text><Text size="sm" c="dimmed">Los valores pueden incluir decimales y coeficientes negativos.</Text></div><Button size="sm" variant="light" leftSection={<IconCirclePlus size={16} />} disabled={draft.restricciones.length >= 40} onClick={() => update(m => ({ ...m, restricciones: [...m.restricciones, { coeficientes: Array(n).fill(''), signo: '<=', rhs: '' }] }))}>Agregar fila</Button></Group>
      <Stack gap="sm">{draft.restricciones.map((row, r) => <Card key={r} className="constraint-card" withBorder>
        <Group align="end" wrap="nowrap" className="constraint-row">
          <Text className="row-number">R{r + 1}</Text>
          {vars.map((name, c) => <NumberInput key={name} label={name} aria-label={`${name} en restricción ${r + 1}`} value={row.coeficientes[c]} error={errors.some(item => item.includes(`${name} en la restricción ${r + 1}`)) ? 'Requerido' : null} onChange={value => update(m => ({ ...m, restricciones: m.restricciones.map((item, j) => j === r ? { ...item, coeficientes: item.coeficientes.map((v, k) => k === c ? String(value) : v) } : item) }))} allowNegative hideControls decimalSeparator="." />)}
          <Select aria-label={`Signo de restricción ${r + 1}`} data={[{ value: '<=', label: '≤' }, { value: '>=', label: '≥' }, { value: '=', label: '=' }]} value={row.signo} onChange={value => update(m => ({ ...m, restricciones: m.restricciones.map((item, j) => j === r ? { ...item, signo: value || '<=' } : item) }))} allowDeselect={false} className="sign-select" />
          <NumberInput label="Lado derecho" aria-label={`Lado derecho restricción ${r + 1}`} value={row.rhs} error={errors.some(item => item.includes(`lado derecho de la restricción ${r + 1}`)) ? 'Requerido' : null} onChange={value => update(m => ({ ...m, restricciones: m.restricciones.map((item, j) => j === r ? { ...item, rhs: String(value) } : item) }))} allowNegative hideControls decimalSeparator="." />
          <Tooltip label={draft.restricciones.length > 1 ? 'Quitar restricción' : 'Debe quedar una restricción'}><ActionIcon color="red" variant="subtle" size="lg" disabled={draft.restricciones.length <= 1} aria-label={`Quitar restricción ${r + 1}`} onClick={() => update(m => ({ ...m, restricciones: m.restricciones.filter((_, j) => j !== r) }))}><IconMinus size={18} /></ActionIcon></Tooltip>
        </Group>
      </Card>)}</Stack>
      <Group justify="space-between" mt="md"><Text size="xs" c="dimmed">{draft.restricciones.length} de 40 restricciones · Variables no negativas</Text><Button variant="gradient" gradient={{ from: 'cyan.5', to: 'indigo.5', deg: 120 }} leftSection={<IconPlayerPlay size={17} />} onClick={onSolve} loading={busy}>Preparar y resolver</Button></Group>
    </Card>
  </Stack></fieldset>;
}

function PreparationView({ payload, result, onContinue }) {
  const prep = result.preparacion || {};
  const names = prep.variables || [];
  const equations = (prep.filas || []).map((row, i) => prettyEquation(row, names, prep.relaciones_normalizadas?.[i] || '=', prep.rhs?.[i]));
  return <Stack gap="lg">
    <ViewHeading eyebrow="PREPARACIÓN MATEMÁTICA" title="Del modelo a la forma estándar" description="Revisa la normalización y la base calculadas para los datos ingresados." badge={`Fase ${result.fase}`} />
    <ModelCard model={payload} />
    <Card className="surface-card" withBorder>
      <Group justify="space-between" mb="md"><Text fw={700}>Forma estándar</Text><Badge color="violet" variant="light">{prep.convencion || 'Variables auxiliares'}</Badge></Group>
      <Stack gap="xs">{equations.map((equation, i) => <Text key={i} className="equation">R{i + 1}: {equation}</Text>)}<Text className="equation muted-text">{names.join(', ')} ≥ 0</Text></Stack>
      <SimpleGrid cols={{ base: 1, sm: 3 }} mt="lg">
        <StatCard label="Base inicial" value={prep.base?.join(', ') || '—'} />
        <StatCard label="Holguras" value={prep.holguras?.join(', ') || 'Ninguna'} />
        <StatCard label="Excesos / artificiales" value={[...(prep.excesos || []), ...(prep.artificiales || [])].join(', ') || 'Ninguna'} />
      </SimpleGrid>
      {(prep.signos_invertidos || []).some(Boolean) && <Alert color="yellow" mt="md">Se normalizaron restricciones con lado derecho negativo; el sentido y los coeficientes fueron ajustados por el backend.</Alert>}
    </Card>
    <Card className="surface-card" withBorder>
      <Group justify="space-between" mb="xs"><Text fw={700}>Tableau inicial</Text><Badge color="cyan" variant="light">{result.tabla_inicial?.fase === 1 ? 'Fase I' : 'Fase II'}</Badge></Group>
      <Text size="sm" c="dimmed" mb="md">La tabla proviene del cálculo real del motor. Los valores internos se conservan; aquí se redondean solo para lectura.</Text>
      <Tableau table={result.tabla_inicial} />
    </Card>
    <Group justify="flex-end"><Button rightSection={<IconArrowRight size={16} />} onClick={onContinue}>Ver procedimiento</Button></Group>
  </Stack>;
}

function ViewHeading({ eyebrow, title, description, badge }) {
  return <Group justify="space-between" align="end" wrap="wrap"><div><Badge color="cyan" variant="light">{eyebrow}</Badge><Title order={2} mt="xs">{title}</Title><Text c="dimmed" mt={4}>{description}</Text></div>{badge && <Badge size="lg" variant="gradient" gradient={{ from: 'cyan', to: 'indigo', deg: 110 }}>{badge}</Badge>}</Group>;
}
function StatCard({ label, value }) {
  return <Card className="stat-card" withBorder><Text size="xs" c="dimmed" tt="uppercase">{label}</Text><Text fw={650} mt={5} className="stat-value">{value}</Text></Card>;
}

function ProcedureView({ result, index, setIndex, onResult }) {
  const tables = result.tablas || [];
  const current = tables[index];
  const pivot = current?.pivote;
  const before = pivot ? tables[pivot.tabla_antes] : null;
  const pivotHighlight = before && pivot ? {
    row: before.filas_ids?.indexOf(pivot.fila),
    column: before.columnas?.indexOf(pivot.columna),
  } : null;
  return <Stack gap="lg">
    <ViewHeading eyebrow="RECORRIDO DEL ALGORITMO" title="Procedimiento paso a paso" description="Avanza por las tablas guardadas por el motor y revisa cada pivote o transición." badge={`${index + 1} / ${tables.length || 1}`} />
    <Card className="surface-card" withBorder>
      <Group justify="space-between" align="center" wrap="wrap"><div><Badge color={current?.fase === 1 ? 'violet' : 'cyan'} variant="light">Fase {current?.fase || result.fase}</Badge><Text fw={700} mt="xs">{pivot ? `Iteración ${Math.max(1, index)}` : index === 0 ? 'Tabla inicial' : 'Cambio de fase'}</Text></div><Group><Button variant="default" leftSection={<IconArrowLeft size={16} />} disabled={index <= 0} onClick={() => setIndex(i => Math.max(i - 1, 0))}>Anterior</Button>{index < tables.length - 1 ? <Button rightSection={<IconArrowRight size={16} />} onClick={() => setIndex(i => Math.min(i + 1, tables.length - 1))}>Siguiente</Button> : <Button rightSection={<IconCheck size={16} />} onClick={onResult}>Ver resultado</Button>}</Group></Group>
      <div className="timeline" role="list" aria-label="Tablas de iteración">{tables.map((table, i) => <button key={i} className={`timeline-step ${i === index ? 'active' : ''}`} type="button" aria-current={i === index ? 'step' : undefined} onClick={() => setIndex(i)}><span>{String(i).padStart(2, '0')}</span><small>{table.pivote ? 'Pivote' : i ? 'Fase' : 'Inicio'}</small></button>)}</div>
    </Card>
    {pivot && before && <Card className="surface-card pivot-summary" withBorder>
      <Group gap="xs" mb="sm"><Badge color="teal" variant="light">Entra {pivot.columna}</Badge><Badge color="violet" variant="light">Sale {pivot.saliente}</Badge><Badge color="yellow" variant="light">Pivote {numberText(pivot.valor, 6)}</Badge></Group>
      <Text fw={650} mb="xs">Pivote seleccionado en la tabla anterior</Text><Tableau table={before} highlight={pivotHighlight} />
      <Text fw={650} mt="lg" mb="xs">Razones para elegir la fila saliente</Text>
      <Table.ScrollContainer minWidth={480} type="native"><Table withTableBorder withColumnBorders><Table.Thead><Table.Tr><Table.Th>Fila</Table.Th><Table.Th>Razón</Table.Th><Table.Th>Decisión</Table.Th></Table.Tr></Table.Thead><Table.Tbody>{Object.entries(pivot.razones || {}).map(([row, ratio]) => <Table.Tr key={row} className={row === pivot.fila ? 'leaving-row' : ''}><Table.Th>{row}</Table.Th><Table.Td>{ratio === null ? '—' : numberText(ratio, 8)}</Table.Td><Table.Td><Badge color={ratio === null ? 'gray' : row === pivot.fila ? 'violet' : 'teal'} variant="light">{ratio === null ? 'Excluida' : row === pivot.fila ? 'Razón mínima · sale' : 'Válida'}</Badge></Table.Td></Table.Tr>)}</Table.Tbody></Table></Table.ScrollContainer>
      <Text size="sm" c="dimmed" mt="sm">Las filas con coeficiente entrante no positivo aparecen excluidas y no se usan para elegir el pivote.</Text>
    </Card>}
    <Card className="surface-card" withBorder>
      <Group justify="space-between" mb="xs"><Text fw={700}>Tabla {index} · después de {index === 0 ? 'la preparación' : pivot ? 'la operación' : 'la transición'}</Text><Badge color={current?.fase === 1 ? 'violet' : 'cyan'} variant="light">Fase {current?.fase}</Badge></Group>
      <Tableau table={current} />
    </Card>
    {!!current?.operaciones?.length && <Card className="surface-card" withBorder><Text fw={700} mb="sm">Operaciones realizadas</Text><Stack gap="xs">{current.operaciones.map((op, i) => <Text key={i} className="operation-line"><span>{String(i + 1).padStart(2, '0')}</span>{op}</Text>)}</Stack></Card>}
  </Stack>;
}

function ResultView({ payload, result, recordId, persisted, onSave, busy }) {
  const optimal = result.estado === 'optimal';
  return <Stack gap="lg">
    <ViewHeading eyebrow="ESTADO DEL MODELO" title="Resultado del cálculo" description="El resultado y su interpretación dependen del estado devuelto por el motor." badge={statusLabels[result.estado] || result.estado} />
    <Alert color={optimal ? 'teal' : result.estado === 'infeasible' || result.estado === 'unbounded' ? 'yellow' : 'red'} title={statusLabels[result.estado] || 'Estado reportado'}>{statusDescriptions[result.estado] || 'El servidor devolvió un estado que requiere revisión.'}</Alert>
    <SimpleGrid cols={{ base: 1, sm: optimal ? 3 : 2 }}>
      <StatCard label="Estado" value={statusLabels[result.estado] || result.estado} />
      {optimal && <StatCard label={`Valor ${payload.sentido === 'max' ? 'máximo' : 'mínimo'} de Z`} value={numberText(result.objetivo, 8)} />}
      <StatCard label="Fase final" value={`Fase ${result.fase}`} />
    </SimpleGrid>
    {optimal && <Card className="surface-card" withBorder><Group justify="space-between" mb="md"><Text fw={700}>Variables de decisión</Text><Badge color="teal" variant="light">Solución factible verificada</Badge></Group><SimpleGrid cols={{ base: 2, sm: 3, md: 6 }}>{Object.entries(result.variables || {}).map(([name, value]) => <StatCard key={name} label={name} value={numberText(value, 8)} />)}</SimpleGrid></Card>}
    <ModelCard model={payload} />
    {optimal && <Card className="surface-card" withBorder><Text fw={700} mb="md">Comprobación de restricciones</Text><Table.ScrollContainer minWidth={520} type="native"><Table withTableBorder withColumnBorders><Table.Thead><Table.Tr><Table.Th>Fila</Table.Th><Table.Th>Evaluación</Table.Th><Table.Th>Condición</Table.Th><Table.Th>Estado</Table.Th></Table.Tr></Table.Thead><Table.Tbody>{(result.comprobacion || []).map((row, i) => <Table.Tr key={i}><Table.Th>{row.fila}</Table.Th><Table.Td>{numberText(row.lhs, 8)}</Table.Td><Table.Td>{row.signo} {numberText(row.rhs, 8)}</Table.Td><Table.Td><Badge color={row.cumple ? 'teal' : 'red'}>{row.cumple ? 'Cumple' : 'No cumple'}</Badge></Table.Td></Table.Tr>)}</Table.Tbody></Table></Table.ScrollContainer></Card>}
    {result.estado !== 'optimal' && <Card className="surface-card" withBorder><Text fw={700} mb="xs">Cómo interpretar este estado</Text><Text size="sm" c="dimmed">No se muestra un valor óptimo ni una combinación de variables porque el motor no certificó una solución óptima.</Text></Card>}
    <Group justify="space-between" wrap="wrap"><Text size="sm" c="dimmed">{persisted && recordId ? 'Guardado en el historial.' : 'Este cálculo todavía no está guardado en el historial.'}</Text><Button leftSection={<IconDeviceFloppy size={17} />} onClick={onSave} loading={busy} disabled={persisted}>Guardar en historial</Button></Group>
  </Stack>;
}

function HistoryView({ onOpen, onDuplicate, onDelete, busy, request, historyKey, setHistoryKey }) {
  const [query, setQuery] = useState('');
  const [sense, setSense] = useState('');
  const [status, setStatus] = useState('');
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [target, setTarget] = useState(null);
  const refresh = useCallback(async (signal) => {
    setLoading(true); setError('');
    try {
      const params = new URLSearchParams({ limite: '100' });
      if (query.trim()) params.set('q', query.trim());
      if (sense) params.set('sentido', sense);
      if (status) params.set('estado', status);
      const data = await request(`/modelos?${params}`, 'GET', undefined, { signal });
      setRecords(data);
    } catch (e) { if (e.name !== 'AbortError') setError(e.message); }
    finally { if (!signal?.aborted) setLoading(false); }
  }, [query, sense, status, request]);
  useEffect(() => { const controller = new AbortController(); const timer = setTimeout(() => refresh(controller.signal), 220); return () => { clearTimeout(timer); controller.abort(); }; }, [refresh]);
  async function confirmDelete() { if (target && await onDelete(target.id)) setTarget(null); }
  return <Stack gap="lg">
    <ViewHeading eyebrow="MODELOS GUARDADOS" title="Historial de trabajo" description="Busca, abre, duplica o elimina registros guardados en la base de datos." badge={`${records.length} registros`} />
    <Card className="surface-card" withBorder><Group align="end" grow wrap="wrap"><TextInput label="Buscar por nombre" placeholder="Escribe para filtrar..." leftSection={<IconSearch size={16} />} value={query} onChange={e => setQuery(e.currentTarget.value)} /><Select label="Sentido" clearable value={sense || null} onChange={value => setSense(value || '')} data={[{ value: 'max', label: 'Maximizar' }, { value: 'min', label: 'Minimizar' }]} /><Select label="Estado" clearable value={status || null} onChange={value => setStatus(value || '')} data={Object.entries(statusLabels).map(([value, label]) => ({ value, label }))} /><PasswordInput label="Clave de escritura (si aplica)" placeholder="Opcional" value={historyKey} onChange={event => setHistoryKey(event.currentTarget.value)} /><Button variant="default" leftSection={<IconRefresh size={16} />} onClick={() => refresh()} loading={loading}>Actualizar</Button></Group><Text size="xs" c="dimmed" mt="xs">La clave se conserva solo en esta sesión del navegador.</Text></Card>
    {error && <Alert color="red" title="No se pudo cargar el historial">{error}</Alert>}
    {loading && records.length === 0 && <Card className="surface-card"><Text c="dimmed">Consultando registros…</Text></Card>}
    {!loading && !error && records.length === 0 && <Card className="surface-card empty-state"><IconDatabase size={34} /><Text fw={650} mt="sm">No hay modelos para mostrar</Text><Text size="sm" c="dimmed">Guarda un cálculo o cambia los filtros para continuar.</Text></Card>}
    <SimpleGrid cols={{ base: 1, lg: 2 }}>{records.map(record => <Card className="surface-card history-card" key={record.id} withBorder>
      <Group justify="space-between" align="start"><div><Text fw={700}>{record.nombre}</Text><Text size="xs" c="dimmed" mt={3}>{record.sentido === 'max' ? 'Maximización' : 'Minimización'} · {new Date(record.creado).toLocaleString('es-GT')}</Text></div><Badge color={record.estado === 'optimal' ? 'teal' : record.estado === 'pending' ? 'gray' : 'yellow'} variant="light">{statusLabels[record.estado] || record.estado}</Badge></Group>
      <Text size="sm" c="dimmed" mt="md">{record.modelo?.objetivo?.length || 0} variables · {record.modelo?.restricciones?.length || 0} restricciones{record.estado === 'optimal' ? ` · Z = ${numberText(record.resultado?.objetivo, 6)}` : ''}</Text>
      <Group gap="xs" mt="md"><Button size="xs" leftSection={<IconExternalLink size={15} />} onClick={() => onOpen(record.id)}>Abrir</Button><Button size="xs" variant="light" leftSection={<IconClipboardList size={15} />} onClick={() => onDuplicate(record.id)}>Duplicar</Button><ActionIcon size="lg" variant="subtle" color="red" aria-label={`Eliminar ${record.nombre}`} onClick={() => setTarget(record)}><IconTrash size={17} /></ActionIcon></Group>
    </Card>)}</SimpleGrid>
    <Modal opened={!!target} onClose={() => setTarget(null)} title="Eliminar modelo" centered><Text size="sm">¿Eliminar <b>{target?.nombre}</b> del historial? Esta acción no se puede deshacer.</Text><Group justify="end" mt="lg"><Button variant="default" onClick={() => setTarget(null)}>Cancelar</Button><Button color="red" onClick={confirmDelete} loading={busy}>Eliminar</Button></Group></Modal>
  </Stack>;
}

function App() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [view, setView] = useState('modelo');
  const [draft, setDraftRaw] = useState(() => blankModel());
  const [solved, setSolved] = useState(null);
  const [recordId, setRecordId] = useState(null);
  const [persisted, setPersisted] = useState(false);
  const [tableIndex, setTableIndex] = useState(0);
  const [error, setError] = useState('');
  const [formErrors, setFormErrors] = useState([]);
  const [busy, setBusy] = useState(false);
  const [health, setHealth] = useState(null);
  const [historyKey, setHistoryKeyRaw] = useState(() => sessionStorage.getItem('simplex-history-key') || '');
  const request = useCallback((path, method = 'GET', body, options = {}) => api(path, method, body, { historyKey, ...options }), [historyKey]);
  const setHistoryKey = useCallback(value => { sessionStorage.setItem('simplex-history-key', value); setHistoryKeyRaw(value); }, []);
  const allowed = useMemo(() => new Set(['modelo', 'historial', ...(solved && !solved.stale ? ['preparacion', 'procedimiento', 'resultado'] : [])]), [solved]);
  const setDraft = useCallback(updater => {
    setDraftRaw(current => typeof updater === 'function' ? updater(current) : updater);
    setFormErrors([]);
    setSolved(current => current ? { ...current, stale: true } : current);
    setView('modelo');
  }, []);
  useEffect(() => { request('/health').then(setHealth).catch(e => setHealth({ status: 'error', detail: e.message })); }, [request]);
  function newModel() { setDraftRaw(blankModel()); setSolved(null); setRecordId(null); setPersisted(false); setTableIndex(0); setError(''); setFormErrors([]); setView('modelo'); }
  function loadExample() { setDraft(demoModel); setRecordId(null); setPersisted(false); setError(''); }
  function navigate(id) { if (allowed.has(id)) { setView(id); setMobileOpen(false); setError(''); } }
  async function solve() {
    const issues = validate(draft); setFormErrors(issues); setError('');
    if (issues.length) return;
    const payload = readModel(draft);
    setBusy(true);
    try {
      const result = await request('/resolver', 'POST', payload);
      setSolved({ payload, result, stale: false }); setPersisted(false); setTableIndex(0); setView('preparacion');
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  async function save() {
    if (!solved || solved.stale) return;
    setBusy(true); setError('');
    try {
      let id = recordId;
      if (id) await request(`/modelos/${encodeURIComponent(id)}`, 'PUT', solved.payload);
      else { const created = await request('/modelos', 'POST', solved.payload); id = created.id; setRecordId(id); }
      const saved = await request(`/modelos/${encodeURIComponent(id)}/resolver`, 'POST');
      setSolved(current => ({ ...current, result: saved.result, stale: false })); setPersisted(true);
    } catch (e) { setError(`No se pudo guardar el resultado. ${e.message}`); }
    finally { setBusy(false); }
  }
  async function openRecord(id) {
    setBusy(true); setError('');
    try {
      const record = await request(`/modelos/${encodeURIComponent(id)}`);
      const model = hydrateModel(record.modelo);
      setDraftRaw(model); setRecordId(record.id); setPersisted(Boolean(record.resultado));
      setSolved(record.resultado ? { payload: readModel(model), result: record.resultado, stale: false } : null);
      setTableIndex(0); setView(record.resultado ? 'preparacion' : 'modelo'); setMobileOpen(false);
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  async function duplicateRecord(id) {
    setBusy(true); setError('');
    try { const copy = await request(`/modelos/${encodeURIComponent(id)}/duplicar`, 'POST'); await openRecord(copy.id); }
    catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  async function deleteRecord(id) {
    setBusy(true); setError('');
    try { await request(`/modelos/${encodeURIComponent(id)}`, 'DELETE'); if (recordId === id) { setRecordId(null); setPersisted(false); } return true; }
    catch (e) { setError(e.message); return false; }
    finally { setBusy(false); }
  }
  const activeTitle = navItems.find(item => item.id === view)?.label || 'Modelo';
  return <AppShell header={{ height: 72 }} navbar={{ width: 254, breakpoint: 'sm', collapsed: { mobile: !mobileOpen } }} padding={{ base: 'md', md: 'xl' }}>
    <AppShell.Header className="topbar"><Group h="100%" px={{ base: 'md', md: 'xl' }} justify="space-between">
      <Group gap="sm"><Burger hiddenFrom="sm" opened={mobileOpen} onClick={() => setMobileOpen(open => !open)} size="sm" aria-label="Abrir navegación" /><div className="brand-mark"><IconBrain size={22} /></div><div><Text className="brand-name">SIMPLEX<span>LAB</span></Text><Text className="brand-caption">OPTIMIZACIÓN LINEAL</Text></div></Group>
      <Group gap="sm"><Badge className="api-state" color={health?.status === 'ok' ? 'teal' : health ? 'red' : 'gray'} variant="light" leftSection={<span className="status-dot" />}>{health?.status === 'ok' ? `API ${health.database || 'activa'} · motor ${health.motor || 'activo'}` : health ? 'API no disponible' : 'Conectando'}</Badge>{solved && !solved.stale && <Button size="xs" variant="light" leftSection={<IconDeviceFloppy size={15} />} onClick={save} loading={busy} disabled={persisted}>Guardar</Button>}</Group>
    </Group></AppShell.Header>
    <AppShell.Navbar className="sidebar" p="md"><Stack gap={5}>
      <Text size="xs" c="dimmed" tt="uppercase" fw={700} px="sm" mb="xs">Espacio de trabajo</Text>
      {navItems.map(({ id, label, icon: Icon }) => <Button key={id} variant={view === id ? 'light' : 'subtle'} color={view === id ? 'cyan' : 'gray'} justify="start" leftSection={<Icon size={18} stroke={1.7} />} disabled={!allowed.has(id)} onClick={() => navigate(id)}>{label}{id === 'resultado' && solved && <span className="nav-status">{statusLabels[solved.result.estado]}</span>}</Button>)}
    </Stack><div className="sidebar-bottom"><Divider mb="md" /><Group gap="xs"><div className="pulse-ring" /><Text size="xs" c="dimmed">{health?.status === 'ok' ? 'Conexión lista' : health ? 'Revisa el servidor API' : 'Comprobando servicios'}</Text></Group><Text size="xs" c="dimmed" mt={5}>Método símplex de dos fases</Text></div></AppShell.Navbar>
    <AppShell.Main className="main-area"><div className="page-head"><div><Text size="xs" c="cyan.3" tt="uppercase" fw={700} className="overline">LABORATORIO DE OPERACIONES</Text><Text size="sm" c="dimmed">{activeTitle} / Sistema Simplex</Text></div>{solved && <Badge variant="outline" color={solved.stale ? 'yellow' : 'cyan'}>{solved.stale ? 'Resultado anterior · requiere recalcular' : statusLabels[solved.result.estado]}</Badge>}</div>
      {error && <Alert className="global-alert" color="red" title="No se completó la operación" withCloseButton onClose={() => setError('')}>{error}</Alert>}
      {view === 'modelo' && <ModelEditor draft={draft} setDraft={setDraft} onSolve={solve} busy={busy} errors={formErrors} onDemo={loadExample} onClear={newModel} />}
      {view === 'preparacion' && solved && <PreparationView payload={solved.payload} result={solved.result} onContinue={() => { setView('procedimiento'); setTableIndex(0); }} />}
      {view === 'procedimiento' && solved && <ProcedureView result={solved.result} index={tableIndex} setIndex={setTableIndex} onResult={() => setView('resultado')} />}
      {view === 'resultado' && solved && <ResultView payload={solved.payload} result={solved.result} recordId={recordId} persisted={persisted} onSave={save} busy={busy} />}
      {view === 'historial' && <HistoryView onOpen={openRecord} onDuplicate={duplicateRecord} onDelete={deleteRecord} busy={busy} request={request} historyKey={historyKey} setHistoryKey={setHistoryKey} />}
      <footer className="page-footer"><Text size="xs" c="dimmed">Simplex Lab <span>·</span> Cálculo conectado al backend del proyecto</Text><Text size="xs" c="dimmed">Los estados sin óptimo no muestran valores de solución.</Text></footer>
    </AppShell.Main>
  </AppShell>;
}

export default App;
