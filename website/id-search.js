// Census indexes are fetched on demand, never during initial map loading.
export function parseCensusQuery(query) {
  const clean = query.trim().replace(/^(?:common(?:[_\s-]*id)?|tract|census(?:\s+tract)?|setor)\s*[:#]?\s*/i, '');
  if (/^g_[0-9a-f]{24}$/i.test(clean)) return {kind:'common',id:clean.toLowerCase(),shard:'g-'+clean.slice(2,4).toLowerCase()};
  if (!/^\d+$/.test(clean)) return null;
  if (clean.length === 15) return {kind: 'tract', id: clean, shard: clean.slice(0, 2)};
  if (clean.length <= 6) {
    const id = String(Number(clean));
    return {kind: 'common', id, shard: String(Math.floor(Number(id) / 10000))};
  }
  return {kind: 'invalid'};
}
export async function findCensusArea(parsed, signal) {
  if (parsed.kind === 'invalid') return null;
  const response = await fetch(`./data/id-search/${parsed.kind}-${parsed.shard}.json`, {signal,cache:'no-store'});
  if (response.status === 404) return null;
  if (!response.ok) throw new Error('Census lookup unavailable');
  const index = await response.json();
  const bounds = Object.hasOwn(index, parsed.id) ? index[parsed.id] : null;
  if (!bounds) return null;
  return {
    label: parsed.kind === 'tract' ? `2022 census tract ${parsed.id}` : `Common area ${parsed.id}`,
    bounds,
    longitude: (bounds[0] + bounds[2]) / 2,
    latitude: (bounds[1] + bounds[3]) / 2
  };
}
