import { loadDataSummaries } from './data-summaries.js?v=20261007-obras-screened';
import { parseCensusQuery, findCensusArea } from './id-search.js?v=20261007-obras-screened';
import { createSocialIndicators } from "./social-indicators.js?v=20261007-obras-screened";
import maplibregl from "./vendor/maplibre-gl.mjs";
import { PMTiles, Protocol } from "./vendor/pmtiles.mjs";
import { RotateCcw, ContactRound, Grid2X2, Blocks, Building2, Wallet, BookOpen, Droplets, Info, Network, Trash2, UserRound, UsersRound, Waves, ChartNoAxesCombined, ChevronLeft, ChevronRight, createIcons, Hexagon, House, Landmark, Leaf, Map as MapIcon, MapPin, Route, Search, TrendingUp } from "./vendor/lucide.mjs";

// SECTION: Public-map contract
// CONTRACT: The browser needs this compact manifest before the optional stats
// request resolves. Keeping it local makes a slow summary response incapable
// of delaying the first usable map.
const socialResponse = await fetch('./data/social.json', {cache:'no-store'});
if (!socialResponse.ok) throw new Error('Census map manifest unavailable');
const SOCIAL_MANIFEST = await socialResponse.json();
const obrasResponse = await fetch('./data/obras-location.json', {cache:'no-store'});
if (!obrasResponse.ok) throw new Error('Obrasgov location manifest unavailable');
const OBRAS_LOCATION = await obrasResponse.json();
const CACHE_REVISION = "2026-10-07-obras-screened";
const BRAZIL_BOUNDS = [[-74.5, -35.5], [-32.5, 6.2]];
const BRAZIL_SOURCE_BOUNDS = [-74.5, -35.5, -32.5, 6.2];
const OPENING_VIEW = { center: [-43.276, -22.930], zoom: 11.0, bearing: -18, pitch: 55, duration: 1300 };
const TYPE_COLOURS = {
  obras: ["#007c91", "#e06c3b", "#755bb7", "#15803d", "#c24174", "#9a6700", "#2364aa", "#b45309", "#0f766e", "#7c3aed"],
  ibama: ["#1e5f74", "#c05621", "#5b4b8a", "#2f855a", "#b83280", "#8b5e00", "#2b6cb0", "#9c4221", "#0f766e", "#6b46c1"],
};
const ENGLISH = {
  "Infraestrutura Hídrica, Portos, Hidrovia": "Water infrastructure, ports and waterways", "Infraestrutura Urbana e Mobilidade": "Urban infrastructure and mobility", "Educação": "Education", "Saúde": "Health", "Desenvolvimento": "Development", "Rodovia": "Roads", "Defesa Civil": "Civil defence", "Defesa civil": "Civil defence", "Administrativo": "Administration", "Esporte": "Sport", "Assistência Social": "Social assistance", "Cultura": "Culture", "Segurança Pública": "Public safety", "Meio Ambiente": "Environment", "Agricultura e Organização Agrária": "Agriculture and land organisation", "Defesa Nacional": "National defence", "Trabalho e Emprego": "Work and employment", "Aviação Civil": "Civil aviation", "Energia": "Energy", "Indústria, Serviços e Comércio Exterior": "Industry, services and foreign trade", "Ciência, Tecnologia e Inovação": "Science, technology and innovation", "Comunicações": "Communications", "Ferrovia": "Railways", "Previdência Social": "Social security",
  "Estruturas Rodoviárias": "Road infrastructure", "Sistema de distribuição": "Distribution system", "Mineração": "Mining", "Empreendimento Agropecuário": "Agricultural project", "Sistema de transmissão": "Transmission system", "Estruturas Ferroviárias": "Rail infrastructure", "Petróleo e Gás - Aquisição": "Oil and gas — acquisition", "Cabo Óptico": "Optical cable", "Usina eólica offshore": "Offshore wind farm", "Transporte Hidroviário Marítimo": "Maritime water transport", "Central de geração hidrelétrica": "Hydroelectric generation plant", "Petróleo e Gás - Perfuração": "Oil and gas — drilling", "Usina hidrelétrica": "Hydroelectric power plant", "Usina eólica": "Wind farm", "Posto de Abastecimento": "Fuel station", "Pequena central hidrelétrica": "Small hydroelectric plant", "Sistema de Abastecimento de Água": "Water supply system", "Transporte Hidroviário Fluvial": "Inland water transport", "Antenas": "Antennas", "Instalação Nuclear/Radiativa": "Nuclear or radiological facility", "Irrigação": "Irrigation", "Petróleo e Gás - Produção": "Oil and gas — production", "Base Aeroespacial": "Aerospace base", "Petróleo e Gás - Onshore": "Oil and gas — onshore", "Aeroporto": "Airport", "Complexo Turístico": "Tourism complex", "Duto terrestre": "Land pipeline", "Sistema de Esgotamento Sanitário": "Sanitation system", "Aterro Sanitário": "Sanitary landfill", "Carcinicultura": "Shrimp farming", "Transposição": "Water transfer",
  id_projeto_investimento: "Investment project ID", desc_nome: "Project name", tipo: "Project type", subtipo: "Project subtype", situacao: "Status", uf_principal: "Primary state", organizacao_resp: "Responsible organisation", vl_investimento_previsto_total: "Planned investment", dt_inicial_prevista: "Planned start", dt_final_prevista: "Planned finish", objectid: "Record ID", no_empreendimento: "Project name", tp_sector_en: "Sector", tp_tipologia: "Project type", nu_sei_formatado: "SEI reference", no_empreendedor: "Project owner", licencas: "Licences", url_licencas_emitidas: "Issued licences",
};
const MANIFEST = {
  datasets: [
    { key: "obras", label: "Obras.gov projects", sourceLayer: "projects_st", typeField: "tipo", types: ["Infraestrutura Hídrica, Portos, Hidrovia", "Infraestrutura Urbana e Mobilidade", "Educação", "Saúde", "Desenvolvimento", "Rodovia", "Defesa Civil", "Administrativo", "Esporte", "Assistência Social", "Cultura", "Segurança Pública", "Meio Ambiente", "Agricultura e Organização Agrária", "Defesa Nacional", "Trabalho e Emprego", "Aviação Civil", "Not specified", "Energia", "Indústria, Serviços e Comércio Exterior", "Ciência, Tecnologia e Inovação", "Comunicações", "Ferrovia", "Defesa civil", "Previdência Social", "Petróleo, Gás e outros HCs"].map((label) => ({ label })) },
    { key: "ibama", label: "IBAMA licensed projects", sourceLayer: "licensed_projects_st", typeField: "tp_tipologia", types: ["Estruturas Rodoviárias", "Sistema de distribuição", "Mineração", "Empreendimento Agropecuário", "Sistema de transmissão", "Estruturas Ferroviárias", "Petróleo e Gás - Aquisição", "Cabo Óptico", "Usina eólica offshore", "Transporte Hidroviário Marítimo", "Central de geração hidrelétrica", "Petróleo e Gás - Perfuração", "Usina hidrelétrica", "Usina eólica", "Posto de Abastecimento", "Pequena central hidrelétrica", "Sistema de Abastecimento de Água", "Transporte Hidroviário Fluvial", "Antenas", "Instalação Nuclear/Radiativa", "Irrigação", "Petróleo e Gás - Produção", "Base Aeroespacial", "Petróleo e Gás - Onshore", "Aeroporto", "Complexo Turístico", "Duto terrestre", "Sistema de Esgotamento Sanitário", "Aterro Sanitário", "Carcinicultura", "Transposição"].map((label) => ({ label })) },
  ],
  census: { key: "census", years: [
    { key: "census-2010", midKey: "census-2010-mid", year: 2010, sourceLayer: "black_ratio_2010_sf", overviewSourceLayer: "black_ratio_2010_municipal", featureCount: 310114 },
    { key: "census-2022", midKey: "census-2022-mid", year: 2022, sourceLayer: "black_ratio_2022_sf", overviewSourceLayer: "black_ratio_2022_municipal", featureCount: 462759 },
  ], change: { key: "census-change", sourceLayer: "black_change_sf", overviewSourceLayer: "black_change_municipal", featureCount: 468142, regions: ["north", "northeast-west", "northeast-east", "minas-espirito-santo", "rio-de-janeiro", "sao-paulo", "south", "centre-west"] } },
  favelas: { key: "favelas", label: "IBGE favelas and communities", sourceLayer: "favelas_2022", featureCount: 12348 },
};
const BASEMAPS = { dark: "https://tiles.openfreemap.org/styles/dark", light: "https://tiles.openfreemap.org/styles/positron", osm: "https://tiles.openfreemap.org/styles/liberty" };
// CONTRACT: These archive bounds prevent MapLibre from requesting every
// regional comparison archive when a visitor only sees one part of Brazil.
const CHANGE_REGION_BOUNDS = SOCIAL_MANIFEST.regional_bounds;

const dom = Object.fromEntries(["obrasCount", "ibamaCount", "favelasCount", "censusCount", "changeCount", "obrasLegend", "ibamaLegend", "favelasToggle", "censusToggle", "censusYear", "censusOpacity", "censusOpacityValue", "changeToggle", "changeOpacity", "changeOpacityValue", "layerPanel", "panelCollapse", "mapLoading", "mapLoadingText", "retryMap", "emptyMapHint", "threeDToggle", "zoomNotice", "openInsights", "dataDrawer", "closeInsights", "summaryCards", "timelineField", "timelineStart", "timelineEnd", "timelineReset", "timelineTitleLine", "timelineCoverage", "timelineChart", "timelineNote", "locationSearch", "locationSearchInput", "locationSearchStatus", "locationSearchResults"].map((id) => [id, document.getElementById(id)]));
const state = { datasets: MANIFEST.datasets, census: MANIFEST.census, favelas: MANIFEST.favelas, visible: { obras: true, ibama: false, favelas: true, census: false, change: false }, censusYear: "2022", censusOpacity: 1, changeOpacity: 1, basemap: "osm", panelCollapsed: false, summariesOpen: false, threeDimensional: true, openingFlightStarted: false, mapTilesLoading: true, registeredSources: new Set(), projectSources: new Map(), projectAttempts: new Map(), censusSources: new Map(), censusAttempts: new Map(), changeSources: new Map(), changeAttempts: new Map(), geocode: { controller: null, inputTimer: null, lastRequestAt: 0, requestId: 0 }, zoomNoticeTimer: null, activePopup: null, activePopupFloats: false, booted: false, timeline: null, timelineArmed: false, recentPointerPick: 0 };

let social;
state.visible.social = false;
const protocol = new Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);
const map = new maplibregl.Map({ container: "map", style: BASEMAPS.osm, center: OPENING_VIEW.center, zoom: OPENING_VIEW.zoom, bearing: OPENING_VIEW.bearing, pitch: OPENING_VIEW.pitch, minZoom: 2, maxZoom: 17, attributionControl: false });
map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "top-right");
map.addControl(new maplibregl.ScaleControl({ maxWidth: 110, unit: "metric" }), "bottom-right");
map.addControl(new maplibregl.AttributionControl({ compact: true }), "bottom-right");
new ResizeObserver(() => map.resize()).observe(document.getElementById("map"));

function pmtilesUrl(key) { return `pmtiles://data/${key === "obras" ? OBRAS_LOCATION.archive : key + ".pmtiles"}?v=${CACHE_REVISION}`; }
function text(value) { return ENGLISH[value] || value || "Not specified"; }
function integer(value) { return new Intl.NumberFormat("en-US").format(Number(value) || 0); }
function percent(value) { return new Intl.NumberFormat("en-US", { style: "percent", maximumFractionDigits: 1 }).format(Number(value) || 0); }
function selectedCensus() { return state.census.years.find((item) => String(item.year) === state.censusYear); }
const MAX_PROJECT_LOAD_ATTEMPTS = 3;
function clearProjectTimer(source) { const tracked = state.projectSources.get(source); if (!tracked) return; if (tracked.timer) window.clearTimeout(tracked.timer); state.projectSources.set(source, { ...tracked, timer: null }); }
function armProjectTimer(source) {
  const tracked = state.projectSources.get(source);
  if (!tracked || tracked.status !== "loading" || tracked.timer) return;
  const timer = window.setTimeout(() => retryProjectSource(source, "stalled"), 12000);
  state.projectSources.set(source, { ...tracked, timer });
}
function sourceReady(id, label) {
  state.registeredSources.add(id);
  state.projectSources.set(id, { key: id, label, status: "loading", timer: null, attempt: state.projectAttempts.get(id) || 1 });
  armProjectTimer(id);
  refreshMapLoading();
}
function setLoading(message, failed = false) { dom.mapLoadingText.textContent = message; dom.mapLoading.classList.remove("is-ready"); dom.retryMap.hidden = !failed; }
function setReady() { dom.mapLoading.classList.add("is-ready"); }
function sourceIsSelected(sourceId) {
  if (social?.selected(sourceId)) return true;
  if (sourceId === "obras" || sourceId === "ibama" || sourceId === "favelas") return state.visible[sourceId];
  const selected = selectedCensus();
  if (state.visible.census && selected && censusDefinition(selected, censusLevelAtZoom()).source === sourceId) return true;
  return state.visible.change && changeDefinitions(censusLevelAtZoom()).some((definition) => definition.source === sourceId);
}
function typeColour(dataset, label) { const index = dataset.types.findIndex((entry) => entry.label === label); return TYPE_COLOURS[dataset.key][Math.max(index, 0) % TYPE_COLOURS[dataset.key].length]; }
function typeExpression(dataset) { const expression = ["match", ["coalesce", ["get", dataset.typeField], "Not specified"]]; dataset.types.forEach((entry) => expression.push(entry.label, typeColour(dataset, entry.label))); expression.push(TYPE_COLOURS[dataset.key][0]); return expression; }
// WHY: Planned investments span several orders of magnitude. A logarithmic
// scale makes their differences visible without allowing a few large projects
// to hide the rest of the Obras.gov point layer.
function pointRadiusExpression(dataset) {
  const fallback = ["interpolate", ["linear"], ["zoom"], 3, 1.5, 9, 5.3];
  if (dataset.key !== "obras") return fallback;
  const investment = ["ln", ["+", 1, ["max", 0, ["to-number", ["get", "vl_investimento_previsto_total"], 0]]]];
  const radius = ["interpolate", ["linear"], investment, 0, 2, Math.log(100000), 2.7, Math.log(1000000), 3.7, Math.log(10000000), 5, Math.log(100000000), 6.7, Math.log(1000000000), 8.4, Math.log(10000000000), 10];
  return ["interpolate", ["linear"], ["zoom"], 3, ["*", .45, radius], 9, radius, 14, ["*", 1.3, radius]];
}
function ratioExpression() { return ["interpolate", ["linear"], ["coalesce", ["get", "black_ratio"], 0], 0, "#f3f0eb", .1, "#b6c0bf", .25, "#6d8f90", .5, "#205b65", 1, "#0c2635"]; }
function ratioChangeExpression() { return ["interpolate", ["linear"], ["coalesce", ["get", "black_ratio_change"], 0], -1, "#9e2f44", -.25, "#de7a70", -.05, "#f4d4cb", 0, "#f7f7f7", .05, "#c8e1e5", .25, "#5a98a5", 1, "#1d6274"]; }
function layerIds(key) { return key === "obras" ? ["obras-line", "obras-point"] : [`${key}-fill`, `${key}-line`, `${key}-point`]; }
function favelasLayerIds() { return ["favelas-fill", "favelas-line"]; }
function censusLayerIds(year) { return [`${year.key}-overview`, `${year.key}-mid`, `${year.key}-detail`]; }
function changeLayerIds() { return ["census-change-overview", ...state.census.change.regions.flatMap((region) => [`census-change-mid-${region}`, `census-change-detail-${region}`])]; }
function censusDefinition(year, level) { return level === "overview" ? { level, source: `${year.key}-overview`, layer: `${year.key}-overview`, sourceLayer: year.overviewSourceLayer } : level === "mid" ? { level, source: year.midKey, layer: `${year.key}-mid`, sourceLayer: year.sourceLayer } : { level, source: year.key, layer: `${year.key}-detail`, sourceLayer: year.sourceLayer }; }
function changeDefinition(level, region = null) { const change = state.census.change; if (level === "overview") return { level, source: `${change.key}-overview`, layer: `${change.key}-overview`, sourceLayer: change.overviewSourceLayer, bounds: BRAZIL_SOURCE_BOUNDS }; const suffix = region ? `-${region}` : ""; return { level, region, source: `${change.key}${level === "mid" ? "-mid" : ""}${suffix}`, layer: `${change.key}${level === "mid" ? "-mid" : "-detail"}${suffix}`, sourceLayer: change.sourceLayer, bounds: CHANGE_REGION_BOUNDS[region] }; }
function changeDefinitions(level) { return level === "overview" ? [changeDefinition(level)] : state.census.change.regions.map((region) => changeDefinition(level, region)); }
function censusLevelAtZoom(zoom = map.getZoom()) { return zoom < 7 ? "overview" : zoom < 10 ? "mid" : "detail"; }
const MAX_CENSUS_LOAD_ATTEMPTS = 3;

// SECTION: Shared map-loading feedback
// INVARIANT: A source is ready after MapLibre reports its first tile-content
// event, never merely because its source definition has been accepted by the
// style. Waiting for a whole tiled source to go idle would leave this badge up
// while a usable map keeps requesting tiles during pan and zoom.
function refreshMapLoading() {
  const socialStatus = social?.status();
  if (socialStatus) { setLoading(socialStatus.message, socialStatus.failed); return; }
  const selected = selectedCensus();
  if (state.visible.census && selected) {
    const definition = censusDefinition(selected, censusLevelAtZoom());
    const tracked = state.censusSources.get(definition.source);
    if (tracked?.status === "failed") { setLoading(`${censusLabel(selected, definition.level)} failed to load.`, true); return; }
    if (!tracked || tracked.status !== "ready") { setLoading(`Loading ${censusLabel(selected, definition.level)}…`); return; }
  }
  if (state.visible.change) {
    const definitions = changeDefinitions(censusLevelAtZoom()).filter((definition) => {
      const [west, south, east, north] = definition.bounds;
      const viewport = map.getBounds();
      return west <= viewport.getEast() && east >= viewport.getWest() && south <= viewport.getNorth() && north >= viewport.getSouth();
    });
    const failed = definitions.find((definition) => state.changeSources.get(definition.source)?.status === "failed");
    if (failed) { setLoading(`${changeLabel(failed.level)} failed to load.`, true); return; }
    if (definitions.some((definition) => state.changeSources.get(definition.source)?.status !== "ready")) { setLoading(`Loading ${changeLabel(censusLevelAtZoom())}…`); return; }
  }
  const pendingProject = [...state.projectSources.entries()]
    .find(([key, source]) => state.visible[key] && source.status !== "ready")?.[1];
  const failedProject = [...state.projectSources.entries()]
    .find(([key, source]) => state.visible[key] && source.status === "failed")?.[1];
  if (failedProject) { setLoading(`${failedProject.label} failed to load.`, true); return; }
  if (pendingProject) { setLoading(`Loading ${pendingProject.label}…`); return; }
  // INVARIANT: A source's first content event means it can draw, not that the
  // active viewport has completed its PMTiles requests. Keep feedback visible
  // through MapLibre's next idle event so the visible map is actually settled.
  if (state.mapTilesLoading && Object.values(state.visible).some(Boolean)) { setLoading("Finishing visible map tiles…"); return; }
  setReady();
}
// SECTION: Empty-map guidance
// WHY: With no costly source selected at startup, a short prompt explains the
// intentional empty state without obscuring the basemap or map controls.
function syncEmptyMapHint() { dom.emptyMapHint.hidden = Object.values(state.visible).some(Boolean); }

// SECTION: Map source lifecycle
// INVARIANT: A source is created only after its layer is selected and only
// within a useful zoom range. This prevents invisible archives from competing
// with the map's first visible PMTiles request.
function addProjectDataset(dataset) {
  if (map.getSource(dataset.key)) return;
  sourceReady(dataset.key, dataset.label);
  map.addSource(dataset.key, { type: "vector", url: pmtilesUrl(dataset.key) });
  const base = { source: dataset.key, "source-layer": dataset.sourceLayer, layout: { visibility: state.visible[dataset.key] ? "visible" : "none" } };
  // DISPLAY POLICY: Obrasgov polygons are excluded by researcher request; source records remain intact.
  if (dataset.key !== "obras") map.addLayer({ ...base, id: `${dataset.key}-fill`, type: "fill", filter: ["==", ["geometry-type"], "Polygon"], paint: { "fill-color": typeExpression(dataset), "fill-opacity": .26, "fill-outline-color": typeExpression(dataset) } });
  map.addLayer({ ...base, id: `${dataset.key}-line`, type: "line", filter: ["==", ["geometry-type"], "LineString"], paint: { "line-color": typeExpression(dataset), "line-width": ["interpolate", ["linear"], ["zoom"], 3, .65, 11, 2.7], "line-opacity": .9 } });
  map.addLayer({ ...base, id: `${dataset.key}-point`, type: "circle", filter: ["==", ["geometry-type"], "Point"], paint: { "circle-color": typeExpression(dataset), "circle-radius": pointRadiusExpression(dataset), "circle-opacity": .86, "circle-stroke-color": "#f8fbfb", "circle-stroke-width": ["interpolate", ["linear"], ["zoom"], 3, 0, 8, .8] } });
}
// SECTION: Favela and community source lifecycle
// INVARIANT: Community polygons stay below project features but above the
// census layers, preserving the existing project-over-context visual order.
function addFavelasLayer() {
  const dataset = state.favelas;
  if (!map.getSource(dataset.key)) {
    sourceReady(dataset.key, dataset.label);
    map.addSource(dataset.key, { type: "vector", url: pmtilesUrl(dataset.key), bounds: BRAZIL_SOURCE_BOUNDS });
  }
  const before = ["obras-fill", "obras-line", "obras-point"].find(id => map.getLayer(id));
  // The layer may be created during initial boot, before any checkbox change
  // fires. Its visibility must therefore follow state immediately.
  const visibility = state.visible.favelas ? "visible" : "none";
  if (!map.getLayer("favelas-fill")) map.addLayer({ id: "favelas-fill", type: "fill", source: dataset.key, "source-layer": dataset.sourceLayer, layout: { visibility }, paint: { "fill-antialias": false, "fill-color": "#c0265f", "fill-opacity": .30 } }, before);
  if (!map.getLayer("favelas-line")) map.addLayer({ id: "favelas-line", type: "line", source: dataset.key, "source-layer": dataset.sourceLayer, layout: { visibility }, paint: { "line-color": "#9d174d", "line-width": ["interpolate", ["linear"], ["zoom"], 4, .35, 12, 1.4], "line-opacity": .88 } }, before);
}
function setFavelasVisible(visible) {
  state.visible.favelas = visible;
  if (visible) addFavelasLayer();
  if (visible) armProjectTimer("favelas"); else clearProjectTimer("favelas");
  favelasLayerIds().forEach((id) => { if (map.getLayer(id)) map.setLayoutProperty(id, "visibility", visible ? "visible" : "none"); });
  syncEmptyMapHint();
  refreshMapLoading();
}
// SECTION: Progressive census source lifecycle
// INVARIANT: Never replace a visible census tier with an unloaded one. This
// avoids blank map states during PMTiles directory/range requests at z7 and z10.
function censusLabel(year, level) { return `IBGE ${year.year} ${level === "overview" ? "municipality overview" : level === "mid" ? "simplified census tracts" : "detailed census tracts"}`; }
function clearCensusTimer(source) { const tracked = state.censusSources.get(source); if (tracked?.timer) window.clearTimeout(tracked.timer); }
function censusReady(definition) { return state.censusSources.get(definition.source)?.status === "ready"; }
function trackCensusSource(year, definition) {
  const tracked = state.censusSources.get(definition.source);
  if (tracked?.status === "ready" || tracked?.status === "loading" || tracked?.status === "failed") return;
  const timer = window.setTimeout(() => retryCensusLevel(year, definition.level, "stalled"), 12000);
  state.censusSources.set(definition.source, { year, definition, status: "loading", timer, attempt: state.censusAttempts.get(definition.source) || 1 });
  refreshMapLoading();
}
function addCensusLevel(year, level) {
  const definition = censusDefinition(year, level);
  const sourceWasAdded = !map.getSource(definition.source);
  if (sourceWasAdded) map.addSource(definition.source, { type: "vector", url: pmtilesUrl(definition.source) });
  if (!map.getLayer(definition.layer)) {
    const before = ["obras-fill", "obras-line", "obras-point"].find(id => map.getLayer(id));
    map.addLayer({ id: definition.layer, type: "fill", source: definition.source, "source-layer": definition.sourceLayer, layout: { visibility: "none" }, paint: { "fill-antialias": false, "fill-color": ratioExpression(), "fill-opacity": state.censusOpacity } }, before);
  }
  trackCensusSource(year, definition);
  // WHY: A source added behind a hidden layer can be treated as idle until a
  // later layout mutation. Making its layer visible for one render pass starts
  // the PMTiles request without requiring the visitor to toggle IBGE manually.
  if (sourceWasAdded) window.requestAnimationFrame(() => { if (!state.visible.census || selectedCensus() !== year || !map.getLayer(definition.layer)) return; map.setLayoutProperty(definition.layer, "visibility", "visible"); map.triggerRepaint(); window.requestAnimationFrame(ensureCensus); });
  return definition;
}
function retryCensusLevel(year, level, reason = "retry") {
  const definition = censusDefinition(year, level);
  const tracked = state.censusSources.get(definition.source);
  const attempt = tracked?.attempt || state.censusAttempts.get(definition.source) || 1;
  clearCensusTimer(definition.source);
  if (attempt >= MAX_CENSUS_LOAD_ATTEMPTS) {
    state.censusSources.set(definition.source, { year, definition, status: "failed", attempt });
    refreshMapLoading();
    return;
  }
  state.censusAttempts.set(definition.source, attempt + 1);
  state.censusSources.delete(definition.source);
  if (map.getLayer(definition.layer)) map.removeLayer(definition.layer);
  if (map.getSource(definition.source)) map.removeSource(definition.source);
  if (!map.isStyleLoaded()) return;
  setLoading(`${reason === "stalled" ? "Retrying" : "Loading"} ${censusLabel(year, level)}…`);
  addCensusLevel(year, level);
  syncCensusVisibility();
}
function ensureCensus() {
  if (!state.visible.census || !map.isStyleLoaded()) return;
  const year = selectedCensus(); if (!year) return;
  addCensusLevel(year, "overview");
  const desired = censusLevelAtZoom();
  if (desired !== "overview") addCensusLevel(year, desired);
  syncCensusVisibility();
}
function syncCensusVisibility() {
  const selected = selectedCensus(); const desired = selected ? censusLevelAtZoom() : "overview";
  const fallback = desired === "detail" ? ["detail", "mid", "overview"] : desired === "mid" ? ["mid", "overview"] : ["overview"];
  // There is no previous tier on a cold start. Keep the desired layer visible
  // then, so MapLibre begins fetching it instead of waiting for a user toggle.
  const visibleLevel = selected && state.visible.census ? fallback.find((level) => censusReady(censusDefinition(selected, level))) || desired : null;
  // Keep a not-yet-ready tier mounted but transparent while its established
  // fallback remains visible. This warm-loads the next PMTiles archive without
  // producing either a blank map or a redundant manual visibility toggle.
  const warmingLevel = selected && state.visible.census && visibleLevel !== desired ? desired : null;
  state.census.years.forEach((year) => censusLayerIds(year).forEach((id) => { if (!map.getLayer(id)) return; const level = id.endsWith("-overview") ? "overview" : id.endsWith("-mid") ? "mid" : "detail"; const isVisible = year === selected && (level === visibleLevel || level === warmingLevel); map.setLayoutProperty(id, "visibility", isVisible ? "visible" : "none"); map.setPaintProperty(id, "fill-opacity", level === warmingLevel ? 0 : state.censusOpacity); }));
  refreshMapLoading();
}
// A short local opening zoom stays within the detailed census tier.
let openingAnimationActive = false;
function startOpeningFlight() {
  if (state.openingFlightStarted) return;
  state.openingFlightStarted = true;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  openingAnimationActive = true;
  map.once('moveend', () => { openingAnimationActive = false; });
  map.easeTo({ ...OPENING_VIEW });
}
function cancelOpeningZoom() {
  state.openingFlightStarted = true;
  if (openingAnimationActive) { openingAnimationActive = false; map.stop(); }
}
for (const type of ['pointerdown', 'wheel', 'keydown']) {
  document.querySelector('.map-workspace').addEventListener(type, cancelOpeningZoom, { capture: true, passive: true });
}
// INVARIANT: The optional comparison layer follows the same three-tile-tier
// protocol as census ratios, but never competes with the default startup load.
function changeLabel(level) { return `IBGE ratio change ${level === "overview" ? "municipality overview" : level === "mid" ? "simplified comparison areas" : "detailed comparison areas"}`; }
function changeDefinitionInViewport(definition) {
  const [west, south, east, north] = definition.bounds;
  const viewport = map.getBounds();
  return west <= viewport.getEast() && east >= viewport.getWest() && south <= viewport.getNorth() && north >= viewport.getSouth();
}
function activeChangeDefinitions(level = censusLevelAtZoom()) { return changeDefinitions(level).filter(changeDefinitionInViewport); }
const MAX_CHANGE_LOAD_ATTEMPTS = 3;
function clearChangeTimer(source) { const tracked = state.changeSources.get(source); if (tracked?.timer) window.clearTimeout(tracked.timer); }
function changeReady(definition) { return state.changeSources.get(definition.source)?.status === "ready"; }
function trackChangeSource(definition) {
  const tracked = state.changeSources.get(definition.source);
  if (tracked?.status === "ready" || tracked?.status === "loading" || tracked?.status === "failed") return false;
  const timer = window.setTimeout(() => retryChangeSource(definition, "stalled"), 12000);
  state.changeSources.set(definition.source, { definition, status: "loading", timer, attempt: state.changeAttempts.get(definition.source) || 1 });
  refreshMapLoading();
  return true;
}
function addChangeLevel(level) {
  const definitions = changeDefinitions(level);
  definitions.forEach((definition) => {
    const sourceWasAdded = !map.getSource(definition.source);
    if (sourceWasAdded) map.addSource(definition.source, { type: "vector", url: pmtilesUrl(definition.source), bounds: definition.bounds });
    if (!map.getLayer(definition.layer)) {
      const before = censusLayerIds(selectedCensus()).find((id) => map.getLayer(id)) || (map.getLayer("obras-fill") ? "obras-fill" : undefined);
      map.addLayer({ id: definition.layer, type: "fill", source: definition.source, "source-layer": definition.sourceLayer, layout: { visibility: "none" }, paint: { "fill-antialias": false, "fill-color": ratioChangeExpression(), "fill-opacity": state.changeOpacity } }, before);
    }
    const shouldWarm = level === "overview" || changeDefinitionInViewport(definition);
    const newlyTracked = shouldWarm && trackChangeSource(definition);
    if ((sourceWasAdded || newlyTracked) && shouldWarm) {
      // WHY: A new PMTiles source behind a hidden layer can remain idle until a
      // visitor toggles it. Making its layer visible for one render pass
      // initiates the first request without requiring a second click.
      window.requestAnimationFrame(() => { if (!state.visible.change || !map.getLayer(definition.layer)) return; map.setLayoutProperty(definition.layer, "visibility", "visible"); map.triggerRepaint(); window.requestAnimationFrame(ensureChange); });
    }
  });
  return definitions;
}
function retryChangeSource(definition, reason = "retry") {
  const tracked = state.changeSources.get(definition.source);
  const attempt = tracked?.attempt || state.changeAttempts.get(definition.source) || 1;
  clearChangeTimer(definition.source);
  if (attempt >= MAX_CHANGE_LOAD_ATTEMPTS) {
    state.changeSources.set(definition.source, { definition, status: "failed", attempt });
    refreshMapLoading();
    return;
  }
  state.changeAttempts.set(definition.source, attempt + 1);
  state.changeSources.delete(definition.source);
  if (map.getLayer(definition.layer)) map.removeLayer(definition.layer);
  if (map.getSource(definition.source)) map.removeSource(definition.source);
  if (!map.isStyleLoaded() || !state.visible.change) return;
  setLoading(`${reason === "stalled" ? "Retrying" : "Loading"} ${changeLabel(definition.level)}…`);
  addChangeLevel(definition.level);
  syncChangeVisibility();
}
function ensureChange() {
  if (!state.visible.change || !map.isStyleLoaded()) return;
  addChangeLevel("overview");
  const desired = censusLevelAtZoom();
  if (desired !== "overview") addChangeLevel(desired);
  syncChangeVisibility();
}
function syncChangeVisibility() {
  const desired = censusLevelAtZoom();
  const activeSources = new Set(activeChangeDefinitions(desired).map((definition) => definition.source));
  const desiredReady = desired === "overview" || (activeSources.size > 0 && [...activeSources].every((source) => changeReady({ source })));
  const visibleLevel = desiredReady ? desired : "overview";
  // INVARIANT: A regional comparison tile never replaces the nationwide
  // municipality overview until every source covering the current viewport is
  // ready. This makes a transient PMTiles request a seamless fallback, not a
  // blank or indefinitely stalled map state.
  changeLayerIds().forEach((id) => {
    const layer = map.getLayer(id); if (!layer) return;
    const level = id === "census-change-overview" ? "overview" : id.startsWith("census-change-mid-") ? "mid" : "detail";
    const visible = state.visible.change && (level === "overview" ? visibleLevel === "overview" : level === visibleLevel && activeSources.has(layer.source));
    map.setLayoutProperty(id, "visibility", visible ? "visible" : "none");
    map.setPaintProperty(id, "fill-opacity", state.changeOpacity);
  });
  refreshMapLoading();
}
// SECTION: Point, line, and community source recovery
// INVARIANT: Every selectable source gets the same bounded recovery contract.
// A source that stalls without emitting a MapLibre error is recreated, while
// an invisible layer is left dormant until the visitor selects it again.
function retryProjectSource(source, reason = "retry") {
  const tracked = state.projectSources.get(source);
  if (!tracked) return;
  const attempt = tracked.attempt || state.projectAttempts.get(source) || 1;
  clearProjectTimer(source);
  if (attempt >= MAX_PROJECT_LOAD_ATTEMPTS) {
    state.projectSources.set(source, { ...tracked, status: "failed", timer: null, attempt });
    refreshMapLoading();
    return;
  }
  state.projectAttempts.set(source, attempt + 1);
  const ids = source === "favelas" ? favelasLayerIds() : layerIds(source);
  ids.forEach((id) => { if (map.getLayer(id)) map.removeLayer(id); });
  if (map.getSource(source)) map.removeSource(source);
  state.projectSources.delete(source);
  if (!map.isStyleLoaded() || !state.visible[source]) return;
  setLoading(`${reason === "stalled" ? "Retrying" : "Loading"} ${tracked.label}…`);
  if (source === "favelas") addFavelasLayer();
  else {
    const dataset = state.datasets.find((item) => item.key === source);
    if (dataset) addProjectDataset(dataset);
  }
  const visible = state.visible[source] ? "visible" : "none";
  ids.forEach((id) => { if (map.getLayer(id)) map.setLayoutProperty(id, "visibility", visible); });
}
function setProjectVisible(key, visible) {
  state.visible[key] = visible;
  const dataset = state.datasets.find((item) => item.key === key);
  if (visible) addProjectDataset(dataset);
  if (visible) armProjectTimer(key); else clearProjectTimer(key);
  layerIds(key).forEach((id) => { if (map.getLayer(id)) map.setLayoutProperty(id, "visibility", visible ? "visible" : "none"); });
  document.getElementById(`${key}Legend`).hidden = !visible;
  syncEmptyMapHint();
  refreshMapLoading();
}
function rehydrateMap() {
  state.registeredSources.clear(); state.projectSources.forEach((tracked) => { if (tracked.timer) window.clearTimeout(tracked.timer); }); state.projectSources.clear(); state.projectAttempts.clear(); state.censusSources.forEach((tracked) => { if (tracked.timer) window.clearTimeout(tracked.timer); }); state.censusSources.clear(); state.censusAttempts.clear(); state.changeSources.forEach((tracked) => { if (tracked.timer) window.clearTimeout(tracked.timer); }); state.changeSources.clear(); state.changeAttempts.clear();
  // WHY: Obras.gov is substantially larger than the currently visible IBGE
  // tier. Start the selected census source before project-source creation so
  // MapLibre can issue both independent PMTiles requests in parallel rather
  // than placing census behind the initial Obras.gov request queue.
  ensureCensus();
  ensureChange();
  requestAnimationFrame(() => {
    if (state.visible.favelas) addFavelasLayer();
    state.datasets.filter((dataset) => state.visible[dataset.key]).forEach(addProjectDataset);
    ensureCensus();
    ensureChange();
    map.resize();
    map.triggerRepaint();
  });
}

function popupNode(kicker, title, badge, rows, primaryLabel = null, layerKey = "obras") {
  const root = document.createElement("div");
  const k = document.createElement("div"); k.className = "popup-kicker"; k.textContent = kicker;
  const h = document.createElement("h2"); h.className = "popup-title"; h.textContent = title;
  const b = document.createElement("div");
  if (primaryLabel) { b.className = `popup-ratio popup-${layerKey}`; const label = document.createElement("span"); label.textContent = primaryLabel; const value = document.createElement("strong"); value.textContent = badge; b.append(label, value); }
  else { b.className = `popup-type popup-${layerKey}`; b.textContent = badge; }
  const list = document.createElement("dl"); list.className = "popup-list";
  rows.forEach(([label, value]) => { if (value === null || value === undefined || String(value).trim() === "") return; const row = document.createElement("div"); const dt = document.createElement("dt"); const dd = document.createElement("dd"); dt.textContent = label; dd.textContent = value; row.append(dt, dd); list.append(row); });
  root.append(k, ...(primaryLabel ? [b, h] : [h, b]), list); return root;
}
function projectPopup(feature, dataset) {
  const p = feature.properties || {}; const name = p.desc_nome || p.no_empreendimento || p.id_projeto_investimento || p.objectid || "Selected project";
  return popupNode(dataset.label, name, `Project type · ${text(p[dataset.typeField])}`, Object.entries(p).filter(([key]) => !["source_row", "location_status", "primary_state_check"].includes(key)).map(([key, value]) => [text(key), key === "vl_investimento_previsto_total" && Number.isFinite(Number(value)) ? new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 }).format(Number(value)) : text(value)]).concat(dataset.key === "obras" ? [["Location screen", p.location_status === "administrative_or_coordinate_review" ? "Retained; location needs review" : "Eligible; position not independently verified"], ["Primary state coverage", text(p.primary_state_check)]] : []), null, dataset.key);
}
function favelasPopup(feature) {
  const p = feature.properties || {};
  const rows = [["Community code", p.cd_fcu], ["Municipality", p.nm_mun], ["State", p.sigla_uf], ["Municipality code", p.cd_mun]];
  return popupNode("IBGE favelas and communities", p.nm_fcu || "Selected community", "Favela and community", rows, null, "favelas");
}
function censusPopup(feature, overview) {
  const p = feature.properties || {}; const ratio = Number(p.black_ratio);
  const rows = [["Census year", p.year], ["Municipality", p.name_muni], ["State", p.abbrev_state], ["Area type", p.zone], ["Census tract code", p.code_tract], ["Census population", p.V0001 || p.pessoa03_V001 || p.population], ["Black population", p.raca_V01318 || p.pessoa03_V003 || p.black_population]];
  return popupNode(overview ? "IBGE municipality summary" : "IBGE census tract", p.name_muni || p.code_tract || "Selected census area", Number.isFinite(ratio) ? percent(ratio) : "—", rows, "Black population ratio", "census");
}
function signedPercentagePoints(value) { const points = Number(value); return Number.isFinite(points) ? `${points > 0 ? "+" : ""}${points.toFixed(1)} pp` : "—"; }
function changePopup(feature, overview) {
  const p = feature.properties || {};
  const rows = overview
    ? [["Municipality code", p.code_muni], ["Comparison areas", p.comparison_areas], ["2010 census population", p.pop_2010], ["2010 Black population", p.black_pop_2010], ["2010 Black population ratio", percent(p.black_ratio_2010)], ["2022 census population", p.pop_2022], ["2022 Black population", p.black_pop_2022], ["2022 Black population ratio", percent(p.black_ratio_2022)]]
    : [["Common ID", p.common_id], ["2022 census tract code", p.id_2022], ["2010 comparison ID", p.base_id], ["Geographic relationship", p.relationship], ["2010 census population", p.pop_2010], ["2010 Black population", p.black_pop_2010], ["2010 Black population ratio", percent(p.black_ratio_2010)], ["2022 census population", p.pop_2022], ["2022 Black population", p.black_pop_2022], ["2022 Black population ratio", percent(p.black_ratio_2022)]];
  return popupNode(overview ? "IBGE municipality change summary" : "IBGE census-area change", overview ? `Municipality ${p.code_muni || "comparison"}` : p.id_2022 || "Selected comparison area", signedPercentagePoints(p.black_ratio_change_pp), rows, "Black population-ratio change", "change");
}
// SECTION: Pitched-map popup placement
// WHY: A flat DOM popup can appear to sit behind or on a point in a pitched
// map. Raising it above the anchor preserves a clear visual relationship.
function featureCanFloat(feature) { return ["Point", "MultiPoint", "LineString", "MultiLineString"].includes(feature.geometry?.type); }
function popupOffset() { return state.activePopupFloats && map.getPitch() >= 20 ? [0, -42] : [0, 0]; }
function createFeaturePopup(feature) { const floats = featureCanFloat(feature); const raised = floats && map.getPitch() >= 20; return new maplibregl.Popup({ closeButton: true, maxWidth: "390px", anchor: raised ? "bottom" : undefined, offset: raised ? [0, -42] : [0, 0] }); }
function updatePopupElevation() { state.activePopup?.setOffset(popupOffset()); }
function openFeature(feature, detail, lngLat) {
  state.activePopup?.remove();
  state.activePopupFloats = featureCanFloat(feature);
  state.activePopup = createFeaturePopup(feature).setLngLat(lngLat).setDOMContent(detail.kind === "social" ? social.popup(feature.properties || {}, detail.overview, feature.layer.id) : detail.kind === "census" ? censusPopup(feature, detail.overview) : detail.kind === "change" ? changePopup(feature, detail.overview) : detail.kind === "favelas" ? favelasPopup(feature) : projectPopup(feature, detail.dataset)).addTo(map);
  state.activePopup.on("close", () => { state.activePopup = null; state.activePopupFloats = false; });
}
function featureLabel(feature, detail) { const p = feature.properties || {}; return detail.kind === "social" ? social.label(p, feature.layer.id) : detail.kind === "census" ? `${p.name_muni || p.code_tract || "Census area"} · ${detail.overview ? "municipality overview" : "census tract"}` : detail.kind === "change" ? `${p.id_2022 || p.code_muni || "Comparison area"} · ${detail.overview ? "municipality change summary" : `ratio change ${signedPercentagePoints(p.black_ratio_change_pp)}`}` : detail.kind === "favelas" ? `${p.nm_fcu || p.cd_fcu || "Favela and community"} · ${p.nm_mun || "community"}` : `${detail.dataset.label} · ${p.desc_nome || p.no_empreendimento || p.id_projeto_investimento || p.objectid || "project"}`; }
// SECTION: Feature picking
// WHY: MapLibre replaces style layers during a basemap change. Deriving the
// metadata from the live layer ID avoids a stale parallel registry that could
// make visible records impossible to click after the style lifecycle runs.
function detailForLayer(id) {
  if (social?.ids().includes(id)) return { kind: "social", overview: social.overview(id) };
  if (favelasLayerIds().includes(id)) return { kind: "favelas" };
  const dataset = state.datasets.find((item) => layerIds(item.key).includes(id));
  if (dataset) return { kind: "project", dataset };
  const year = state.census.years.find((item) => censusLayerIds(item).includes(id));
  if (year) return { kind: "census", overview: id === `${year.key}-overview`, year: year.year };
  if (changeLayerIds().includes(id)) return { kind: "change", overview: id === "census-change-overview" };
  return null;
}
function interactiveLayerIds() {
  // The favela outline duplicates its fill geometry, so only the fill joins
  // picking. This keeps a single community click from opening a false
  // two-feature overlap picker.
  return [...(social?.ids() || []), ...state.datasets.flatMap((dataset) => layerIds(dataset.key)), "favelas-fill", ...state.census.years.flatMap((year) => censusLayerIds(year)), ...changeLayerIds()].filter((id) => map.getLayer(id));
}
function pickFeatures(point) {
  const layers = interactiveLayerIds(); if (!layers.length) return [];
  // INVARIANT: A feature chooser represents real overlap at the selected map
  // pixel. Do not expand this query into a nearby hit area: that makes close,
  // unrelated polygons look like competing selections.
  const features = map.queryRenderedFeatures(point, { layers }); const seen = new Set();
  return features.map((feature) => ({ feature, detail: detailForLayer(feature.layer.id) })).filter((item) => { const p = item.feature.properties || {}; const key = `${item.feature.layer.id}:${p.component_id || p.common_id || p.code_tract || p.id_2022 || p.cd_fcu || p.code_muni || p.id_projeto_investimento || p.objectid || p.fid || JSON.stringify(p)}`; if (seen.has(key)) return false; seen.add(key); return Boolean(item.detail); });
}
function openPicker(point) {
  const candidates = pickFeatures(point); if (!candidates.length) return;
  const lngLat = map.unproject(point); if (candidates.length === 1) { openFeature(candidates[0].feature, candidates[0].detail, lngLat); return; }
  state.activePopup?.remove(); const root = document.createElement("div"); root.className = "picker"; const h = document.createElement("h2"); h.textContent = "Select a mapped feature"; const p = document.createElement("p"); p.textContent = `${candidates.length} features overlap here.`; root.append(h, p);
  candidates.slice(0, 12).forEach((candidate) => { const button = document.createElement("button"); const layerKey = candidate.detail.kind === "social" ? "social" : candidate.detail.kind === "census" ? "census" : candidate.detail.kind === "change" ? "change" : candidate.detail.kind === "favelas" ? "favelas" : candidate.detail.dataset.key; button.className = `picker-option picker-${layerKey}`; const label = featureLabel(candidate.feature, candidate.detail); const [kind, ...rest] = label.split(" · "); const category = document.createElement("span"); category.textContent = kind; button.append(category, document.createTextNode(rest.join(" · "))); button.addEventListener("click", () => openFeature(candidate.feature, candidate.detail, lngLat)); root.append(button); });
  state.activePopupFloats = false;
  state.activePopup = new maplibregl.Popup({ closeButton: true, maxWidth: "390px" }).setLngLat(lngLat).setDOMContent(root).addTo(map);
}
function bindFeaturePicking() {
  const surface = map.getCanvasContainer();
  // MapLibre's event.point is authoritative: it already accounts for canvas
  // scaling, browser zoom, and a resized map. The DOM event is a delayed
  // fallback only for browsers that fail to dispatch MapLibre's click event.
  surface.addEventListener("click", (event) => {
    const bounds = surface.getBoundingClientRect();
    const fallbackPoint = { x: event.clientX - bounds.left, y: event.clientY - bounds.top };
    window.setTimeout(() => {
      if (Date.now() - state.recentPointerPick > 80) openPicker(fallbackPoint);
    }, 0);
  }, true);
  map.on("click", (event) => { state.recentPointerPick = Date.now(); openPicker(event.point); });
}
// SECTION: Map-to-page scroll boundary
// WHY: Popup content sits over the map canvas, where a wheel event otherwise
// reaches the document and scrolls readers into the summaries unintentionally.
function bindScrollContainment() {
  const workspace = document.querySelector(".map-workspace");
  workspace.addEventListener("wheel", (event) => {
    const popup = event.target.closest(".maplibregl-popup-content");
    if (!popup) return;
    event.preventDefault(); event.stopPropagation();
    popup.scrollTop += event.deltaY;
  }, { capture: true, passive: false });
}

function renderLegends() {
  state.datasets.forEach((dataset) => { const root = document.getElementById(`${dataset.key}Legend`); root.replaceChildren(); const intro = document.createElement("p"); intro.className = "key-description"; intro.textContent = dataset.key === "obras" ? "Colour indicates project type." : "Colour indicates licence typology."; root.append(intro); dataset.types.slice(0, 4).forEach((entry) => { const row = document.createElement("div"); row.className = "key-row"; const swatch = document.createElement("span"); swatch.className = "swatch"; swatch.style.background = typeColour(dataset, entry.label); const label = document.createElement("span"); label.textContent = text(entry.label); row.append(swatch, label); root.append(row); }); if (dataset.key === "obras") { const key = document.createElement("div"); key.className = "investment-key"; const label = document.createElement("strong"); label.textContent = "Dot size · planned investment"; const scale = document.createElement("div"); scale.className = "investment-scale"; [["R$100k", "small"], ["R$10m", "medium"], ["R$1bn+", "large"]].forEach(([amount, size]) => { const item = document.createElement("div"); const bubble = document.createElement("span"); bubble.className = `investment-bubble ${size}`; const amountLabel = document.createElement("span"); amountLabel.textContent = amount; item.append(bubble, amountLabel); scale.append(item); }); key.append(label, scale); root.append(key); const note = document.createElement("p"); note.className = "key-description"; note.textContent = `${integer(OBRAS_LOCATION.mapComponents)} point/line components eligible for display after location and primary-state checks. Positions are not independently verified.`; root.append(note); } root.hidden = !state.visible[dataset.key]; });
}
function metric(label, value) { const root = document.createElement("div"); const l = document.createElement("span"); const v = document.createElement("strong"); l.textContent = label; v.textContent = value; root.append(l, v); return root; }
function renderSummaries(datasets) {
  dom.summaryCards.replaceChildren(); const expandableLists = [];
  datasets.forEach((dataset) => { const card = document.createElement("article"); card.className = "summary-card"; const header = document.createElement("header"); const heading = document.createElement("h3"); heading.textContent = dataset.label; const badge = document.createElement("span"); badge.className = "summary-badge"; badge.textContent = `${integer(dataset.featureCount)} ${dataset.key === "obras" ? "source records" : "records"}`; header.append(heading, badge); const metrics = document.createElement("div"); metrics.className = "metric-row"; const leading = dataset.types?.[0]; metrics.append(metric(dataset.key === "obras" ? "Mapped source records" : "Mapped in Brazil", integer(dataset.mappableFeatureCount ?? dataset.featureCount)), metric("Distinct types", integer(dataset.types?.length)), metric("Leading type", text(leading?.label || "—"))); const list = document.createElement("div"); list.className = "frequency-list"; const top = dataset.types || []; const maximum = Math.max(...top.map((entry) => entry.count || 0), 1); top.forEach((entry, index) => { const row = document.createElement("div"); row.className = `frequency-row${index > 7 ? " is-extra" : ""}`; const label = document.createElement("div"); label.className = "frequency-label"; const swatch = document.createElement("span"); swatch.className = "swatch"; swatch.style.background = typeColour(dataset, entry.label); const name = document.createElement("span"); name.textContent = text(entry.label); const count = document.createElement("b"); count.textContent = `${integer(entry.count)} · ${(entry.share || 0).toFixed(1)}%`; label.append(swatch, name, count); const track = document.createElement("div"); track.className = "frequency-track"; const bar = document.createElement("span"); bar.style.background = typeColour(dataset, entry.label); bar.style.width = `${Math.max(1, ((entry.count || 0) / maximum) * 100)}%`; track.append(bar); row.append(label, track); list.append(row); }); card.append(header, metrics, list); if (top.length > 8) { const button = document.createElement("button"); button.className = "show-all"; card.append(button); expandableLists.push({ list, button, count: top.length }); } dom.summaryCards.append(card); });
  // CONTRACT: The two datasets are a comparison pair, so their tables must
  // expand and collapse together regardless of which button was pressed.
  const setExpanded = (open) => expandableLists.forEach((entry) => { entry.list.classList.toggle("is-open", open); entry.button.textContent = open ? "Show fewer types" : `Show all ${entry.count} types`; });
  expandableLists.forEach((entry) => entry.button.addEventListener("click", () => setExpanded(!entry.list.classList.contains("is-open"))));
  setExpanded(false);
}

function dateMillis(value) { return Date.parse(`${value}T12:00:00Z`); }
function dateInput(value) { return new Date(value).toISOString().slice(0, 10); }
function dateLabel(value) { return new Intl.DateTimeFormat("en", { month: "short", year: "numeric", timeZone: "UTC" }).format(new Date(value)); }
function timelineFormat() { return state.timeline?.obras?.formats.find((item) => item.key === dom.timelineField.value); }
function timelineBins(format, start, end) { const duration = end - start; const month = 30.44 * 86400000; const years = duration / (365.25 * 86400000); const unit = years > 8 ? "year" : years > 1.5 ? "quarter" : duration > 90 * 86400000 ? "month" : "week"; const bins = new Map(); const bucket = (value) => { const d = new Date(value); if (unit === "year") return Date.UTC(d.getUTCFullYear(), 0, 1); if (unit === "quarter") return Date.UTC(d.getUTCFullYear(), Math.floor(d.getUTCMonth() / 3) * 3, 1); if (unit === "month") return Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), 1); return Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() - d.getUTCDay()); };
  format.points.forEach(([date, count]) => { const value = dateMillis(date); if (value < start || value > end) return; const key = bucket(value); bins.set(key, (bins.get(key) || 0) + count); }); const result = [...bins.entries()].sort((a, b) => a[0] - b[0]).map(([value, count]) => ({ value, count })); return { bins: result, unit, total: result.reduce((sum, item) => sum + item.count, 0) };
}
function renderTimeline() { const format = timelineFormat(); if (!format) return; let start = dateMillis(dom.timelineStart.value), end = dateMillis(dom.timelineEnd.value); const minimum = dateMillis(format.minimum), maximum = dateMillis(format.maximum); if (!Number.isFinite(start) || !Number.isFinite(end) || start > end) { start = minimum; end = maximum; } start = Math.max(minimum, start); end = Math.min(maximum, end); const { bins, total } = timelineBins(format, start, end); const svg = dom.timelineChart; const width = Math.max(580, Math.min(1200, svg.parentElement.clientWidth || 900)); const height = 270, left = 52, right = 16, top = 12, bottom = 38, innerW = width - left - right, innerH = height - top - bottom, maximumCount = Math.max(...bins.map((bin) => bin.count), 1); svg.replaceChildren(); svg.setAttribute("viewBox", `0 0 ${width} ${height}`); const append = (tag, attributes, content) => { const item = document.createElementNS("http://www.w3.org/2000/svg", tag); Object.entries(attributes).forEach(([key, value]) => item.setAttribute(key, value)); if (content !== undefined) item.textContent = content; svg.append(item); return item; };
  [0, .5, 1].forEach((fraction) => { const y = top + innerH - innerH * fraction; append("line", { class: "chart-grid", x1: left, x2: width - right, y1: y, y2: y }); append("text", { class: "chart-label", x: left - 7, y: y + 4, "text-anchor": "end" }, integer(Math.round(maximumCount * fraction))); }); const barW = innerW / Math.max(bins.length, 1); const tickEvery = Math.max(1, Math.ceil(bins.length / (width > 900 ? 9 : 6))); bins.forEach((bin, index) => { const h = (bin.count / maximumCount) * innerH; const x = left + index * barW; const bar = append("rect", { class: "chart-bar", x: x + .5, y: top + innerH - h, width: Math.max(1, barW - 1), height: Math.max(1, h), tabindex: "0" }); const description = `${dateLabel(bin.value)}: ${integer(bin.count)} projects`; bar.setAttribute("aria-label", description); bar.addEventListener("mouseenter", () => { dom.timelineNote.textContent = description; }); bar.addEventListener("focus", () => { dom.timelineNote.textContent = description; }); if (index === 0 || index === bins.length - 1 || index % tickEvery === 0) append("text", { class: "chart-label", x: x + barW / 2, y: height - 13, "text-anchor": "middle" }, dateLabel(bin.value)); }); append("line", { class: "chart-axis", x1: left, x2: width - right, y1: top + innerH, y2: top + innerH }); dom.timelineTitleLine.textContent = `${format.label} · ${dateLabel(start)} — ${dateLabel(end)}`; dom.timelineCoverage.textContent = `${integer(total)} of ${integer(format.coverage)} recorded projects`; dom.timelineNote.textContent = `Bars adapt from years to weeks as the selected period narrows.`; }
function setupTimeline(payload) { state.timeline = payload; const formats = payload.obras?.formats || []; dom.timelineField.replaceChildren(); formats.forEach((format) => { const option = document.createElement("option"); option.value = format.key; option.textContent = format.label; dom.timelineField.append(option); }); const initial = formats.find((format) => format.key === "registered") || formats[0]; if (!initial) return; dom.timelineField.value = initial.key; dom.timelineStart.min = dom.timelineEnd.min = initial.minimum; dom.timelineStart.max = dom.timelineEnd.max = initial.maximum; dom.timelineStart.value = initial.minimum; dom.timelineEnd.value = initial.maximum; [dom.timelineField, dom.timelineStart, dom.timelineEnd, dom.timelineReset].forEach((control) => { control.disabled = false; }); dom.timelineField.addEventListener("change", () => { const format = timelineFormat(); dom.timelineStart.min = dom.timelineEnd.min = format.minimum; dom.timelineStart.max = dom.timelineEnd.max = format.maximum; dom.timelineStart.value = format.minimum; dom.timelineEnd.value = format.maximum; renderTimeline(); }); [dom.timelineStart, dom.timelineEnd].forEach((control) => control.addEventListener("change", renderTimeline)); dom.timelineReset.addEventListener("click", () => { const format = timelineFormat(); dom.timelineStart.value = format.minimum; dom.timelineEnd.value = format.maximum; renderTimeline(); }); new ResizeObserver(renderTimeline).observe(dom.timelineChart.parentElement); renderTimeline(); }

async function fetchJson(path) { const response = await fetch(`${path}?v=${CACHE_REVISION}`, { cache: "force-cache" }); if (!response.ok) throw new Error(`${path} returned ${response.status}`); return response.json(); }
async function loadStats() { try { const payload = await fetchJson("data/stats.json"); state.datasets = payload.datasets; state.census = payload.census; if (payload.favelas?.featureCount) dom.favelasCount.textContent = `${integer(payload.favelas.featureCount)} communities`; payload.datasets.forEach((dataset) => { document.getElementById(`${dataset.key}Count`).textContent = `${integer(dataset.featureCount)} ${dataset.key === "obras" ? "source records" : "records"}`; }); const census = selectedCensus(); dom.censusCount.textContent = `${integer(census.featureCount)} tracts · ${census.year}`; if (payload.census.change) dom.changeCount.textContent = `${integer(payload.census.change.featureCount)} comparison areas`; renderLegends(); renderSummaries(payload.datasets); state.datasets.forEach((dataset) => layerIds(dataset.key).forEach((id) => { if (!map.getLayer(id)) return; const paint = id.endsWith("fill") ? "fill-color" : id.endsWith("line") ? "line-color" : "circle-color"; map.setPaintProperty(id, paint, typeExpression(dataset)); })); } catch (error) { renderLegends(); dom.summaryCards.textContent = "Summary data is temporarily unavailable."; console.error(error); } }
function armTimeline() { if (state.timelineArmed) return; state.timelineArmed = true; loadDataSummaries(fetchJson); fetchJson("data/timeline.json").then(setupTimeline).catch((error) => { dom.timelineNote.textContent = "The temporal profile could not be loaded."; console.error(error); }); }

// SECTION: Transient zoom feedback
// WHY: The zoom level is useful only while its scale is changing. Pointer
// movement and panning must not make this transient feedback reappear.
function hideZoomNoticeSoon() { if (state.zoomNoticeTimer) window.clearTimeout(state.zoomNoticeTimer); state.zoomNoticeTimer = window.setTimeout(() => dom.zoomNotice.classList.remove("is-visible"), 1000); }
function updateZoomNotice() { const zoom = map.getZoom(); const mode = zoom < 7 ? "Municipality overview" : zoom < 10 ? "Simplified census tracts" : "Detailed census tracts"; dom.zoomNotice.textContent = `Zoom ${zoom.toFixed(1)} · ${mode}`; dom.zoomNotice.classList.add("is-visible"); hideZoomNoticeSoon(); }
// SECTION: Perspective view toggle
// WHY: A direct two-state control provides a clear 3D view without requiring
// visitors to discover MapLibre's pitch gesture or navigation affordance.
function renderThreeDimensionalToggle() {
  dom.threeDToggle.classList.toggle("is-active", state.threeDimensional);
  dom.threeDToggle.setAttribute("aria-pressed", String(state.threeDimensional));
  dom.threeDToggle.textContent = state.threeDimensional ? "2D" : "3D";
  const label = state.threeDimensional ? "Switch to overhead 2D view" : "Switch to 3D view";
  dom.threeDToggle.setAttribute("aria-label", label);
  dom.threeDToggle.title = label;
}
function mountThreeDimensionalControl() {
  const navigationGroup = map.getContainer().querySelector(".maplibregl-ctrl-top-right .maplibregl-ctrl-group");
  if (!navigationGroup || dom.threeDToggle.parentElement === navigationGroup) return;
  navigationGroup.append(dom.threeDToggle);
  dom.threeDToggle.hidden = false;
}
function setThreeDimensional(enabled) {
  state.threeDimensional = enabled;
  renderThreeDimensionalToggle();
  map.easeTo({ bearing: enabled ? -18 : 0, duration: 700, essential: true, pitch: enabled ? 55 : 0 });
}
function resetBrazilView() {
  state.threeDimensional = false;
  renderThreeDimensionalToggle();
  map.fitBounds(BRAZIL_BOUNDS, { bearing: 0, duration: 700, essential: true, padding: 60, pitch: 0 });
}
// SECTION: On-demand data summaries
// INVARIANT: Summaries open above the map so their content never changes the
// page position or removes the active geographic view from the background.
function setDataDrawer(open) { state.summariesOpen = open; dom.dataDrawer.hidden = !open; dom.openInsights.setAttribute("aria-expanded", String(open)); if (open) { if (!state.statsRequested) { state.statsRequested = true; void loadStats(); } armTimeline(); window.requestAnimationFrame(renderTimeline); } }
// SECTION: Attribution display
// WHY: MapLibre remembers an expanded attribution disclosure within its control
// markup. Start every map load as the compact, bottom-right information icon.
let attributionTouched = false;
let attributionObserver;
function collapseAttribution() {
  const attribution = map.getContainer().querySelector(".maplibregl-ctrl-attrib");
  if (!attribution || attributionTouched) return;
  if (!attributionObserver) {
    attribution.querySelector('summary')?.addEventListener('click', () => {
      attributionTouched = true;
      attributionObserver.disconnect();
    }, {capture: true, once: true});
    attributionObserver = new MutationObserver(collapseAttribution);
    attributionObserver.observe(attribution, {attributes: true, attributeFilter: ['class', 'open']});
  }
  if (attribution.hasAttribute('open')) attribution.removeAttribute("open");
  attribution.querySelector("details")?.removeAttribute("open");
  if (attribution.classList.contains("maplibregl-compact-show")) attribution.classList.remove("maplibregl-compact-show");
}
// SECTION: Brazil-only location search
// SECURITY: Searches are user-submitted (never autocomplete), rate-limited,
// and hard-filtered to Brazil before any external geocoder request is made.
const OPEN_METEO_GEOCODER_URL = "https://geocoding-api.open-meteo.com/v1/search";
function locationResultLabel(result) { return result.label || result.name || "Unnamed location"; }
function clearLocationResults() { dom.locationSearchResults.replaceChildren(); dom.locationSearchResults.hidden = true; }
function flyToLocation(result) {
  if (result.bounds) {
    const [west, south, east, north] = result.bounds;
    map.fitBounds([[west, south], [east, north]], {padding: 90, maxZoom: 15.5, duration: 850, pitch: 0, bearing: 0});
  } else map.flyTo({ center: [Number(result.longitude), Number(result.latitude)], zoom: 12.5, duration: 850 });
  dom.locationSearchStatus.textContent = `Showing ${locationResultLabel(result)}.`;
  clearLocationResults();
}
function renderLocationResults(results) {
  clearLocationResults();
  if (!results.length) { dom.locationSearchStatus.textContent = "No matching Brazilian location found."; return; }
  results.forEach((result) => {
    const option = document.createElement("button"); option.type = "button"; option.className = "location-result"; option.textContent = locationResultLabel(result); option.addEventListener("click", () => flyToLocation(result)); dom.locationSearchResults.append(option);
  });
  dom.locationSearchResults.hidden = false;
  dom.locationSearchStatus.textContent = `${results.length} Brazilian ${results.length === 1 ? "result" : "results"}. Choose one.`;
}
async function searchBrazilLocation(query) {
  const normalized = query.trim();
  if (normalized.length < 2 && !/^\d$/.test(normalized)) { clearLocationResults(); dom.locationSearchStatus.textContent = "Enter a city name or census ID."; return; }
  state.geocode.controller?.abort();
  const controller = new AbortController(); const requestId = ++state.geocode.requestId; state.geocode.controller = controller;
  clearLocationResults(); dom.locationSearchStatus.textContent = "Searching Brazil…";
  const censusQuery = parseCensusQuery(normalized);
  if (censusQuery) {
    dom.locationSearchStatus.textContent = "Finding census area…";
    try {
      const result = await findCensusArea(censusQuery, controller.signal);
      if (requestId !== state.geocode.requestId) return;
      if (result) renderLocationResults([result]);
      else dom.locationSearchStatus.textContent = "ID not found. Enter a full 15-digit 2022 tract ID or a common ID.";
    } catch (error) {
      if (error.name !== 'AbortError' && requestId === state.geocode.requestId) dom.locationSearchStatus.textContent = "Census search is temporarily unavailable. Please retry.";
    } finally {
      if (requestId === state.geocode.requestId) state.geocode.controller = null;
    }
    return;
  }
  const wait = Math.max(0, 300 - (Date.now() - state.geocode.lastRequestAt));
  if (wait) await new Promise((resolve) => window.setTimeout(resolve, wait));
  if (controller.signal.aborted || requestId !== state.geocode.requestId) return;
  state.geocode.lastRequestAt = Date.now();
  const parameters = new URLSearchParams({ name: normalized, countryCode: "BR", language: "en", format: "json", count: "5" });
  try {
    const response = await fetch(`${OPEN_METEO_GEOCODER_URL}?${parameters}`, { signal: controller.signal, headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`Location search returned ${response.status}`);
    const payload = await response.json();
    if (requestId !== state.geocode.requestId) return;
    const results = (payload.results || []).filter((result) => result?.country_code?.toUpperCase() === "BR" && Number.isFinite(result.latitude) && Number.isFinite(result.longitude)).map((result) => ({ ...result, label: [result.name, result.admin1, result.country].filter(Boolean).join(", ") }));
    renderLocationResults(results);
  } catch (error) {
    if (error.name === "AbortError") return;
    console.error(error); dom.locationSearchStatus.textContent = "Location search is temporarily unavailable.";
  } finally {
    if (requestId === state.geocode.requestId) state.geocode.controller = null;
  }
}
function dismissLocationSearch() { if (state.geocode.inputTimer) window.clearTimeout(state.geocode.inputTimer); state.geocode.inputTimer = null; state.geocode.controller?.abort(); state.geocode.controller = null; ++state.geocode.requestId; clearLocationResults(); dom.locationSearchStatus.textContent = ""; }
function queueLocationSearch() {
  if (state.geocode.inputTimer) window.clearTimeout(state.geocode.inputTimer);
  const query = dom.locationSearchInput.value.trim();
  if (query.length < 2 && !/^\d$/.test(query)) { dismissLocationSearch(); return; }
  state.geocode.controller?.abort(); state.geocode.controller = null; ++state.geocode.requestId; clearLocationResults(); dom.locationSearchStatus.textContent = "";
  state.geocode.inputTimer = window.setTimeout(() => { state.geocode.inputTimer = null; void searchBrazilLocation(query); }, 280);
}
function bindLocationSearch() {
  dom.locationSearch.addEventListener("submit", (event) => { event.preventDefault(); if (state.geocode.inputTimer) window.clearTimeout(state.geocode.inputTimer); state.geocode.inputTimer = null; void searchBrazilLocation(dom.locationSearchInput.value); });
  dom.locationSearchInput.addEventListener("input", queueLocationSearch);
  document.addEventListener("pointerdown", (event) => { if (!dom.locationSearch.contains(event.target)) dismissLocationSearch(); });
}
// SECTION: Control-panel disclosure
// WHY: The map remains usable when controls are not needed, while the compact
// button preserves one-click access without removing any layer controls.
function setPanelCollapsed(collapsed, persist = true) {
  state.panelCollapsed = collapsed;
  dom.layerPanel.classList.toggle("is-collapsed", collapsed);
  dom.panelCollapse.classList.toggle("is-collapsed", collapsed);
  dom.panelCollapse.setAttribute("aria-expanded", String(!collapsed));
  const action = collapsed ? "Expand" : "Collapse";
  dom.panelCollapse.setAttribute("aria-label", `${action} layer controls`);
  dom.panelCollapse.title = `${action} layer controls`;
  dom.panelCollapse.querySelector(".sr-only").textContent = `${action} layer controls`;
  if (persist) {
    try { localStorage.setItem("brazil-map-panel-collapsed", String(collapsed)); } catch { /* Storage is optional for this presentation preference. */ }
  }
  window.setTimeout(() => map.resize(), 180);
}
function restorePanelCollapsed() {
  try { setPanelCollapsed(localStorage.getItem("brazil-map-panel-collapsed") === "true", false); } catch { setPanelCollapsed(false, false); }
}
function bindControls() {
  document.getElementById("obrasToggle").addEventListener("change", (event) => setProjectVisible("obras", event.target.checked)); document.getElementById("ibamaToggle").addEventListener("change", (event) => setProjectVisible("ibama", event.target.checked));
  dom.favelasToggle.addEventListener("change", (event) => setFavelasVisible(event.target.checked));
  dom.censusToggle.addEventListener("change", (event) => { state.visible.census = event.target.checked; ensureCensus(); syncCensusVisibility(); document.querySelector("[data-layer-card='census'] .census-settings").hidden = !state.visible.census; syncEmptyMapHint(); });
  dom.censusYear.addEventListener("change", (event) => { state.censusYear = event.target.value; const year = selectedCensus(); dom.censusCount.textContent = `${integer(year.featureCount)} tracts · ${year.year}`; ensureCensus(); syncCensusVisibility(); });
  dom.censusOpacity.addEventListener("input", (event) => { state.censusOpacity = Number(event.target.value) / 100; dom.censusOpacityValue.textContent = `${event.target.value}%`; syncCensusVisibility(); });
  dom.changeToggle.addEventListener("change", (event) => { state.visible.change = event.target.checked; ensureChange(); syncChangeVisibility(); document.querySelector("[data-layer-card='change'] .census-settings").hidden = !state.visible.change; syncEmptyMapHint(); });
  dom.changeOpacity.addEventListener("input", (event) => { state.changeOpacity = Number(event.target.value) / 100; dom.changeOpacityValue.textContent = `${event.target.value}%`; syncChangeVisibility(); });
  document.getElementById("basemap").addEventListener("change", (event) => { state.basemap = event.target.value; state.activePopup?.remove(); map.setStyle(state.basemap === "satellite" ? { version: 8, sources: { satellite: { type: "raster", tiles: ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"], tileSize: 256, attribution: "Tiles © Esri" } }, layers: [{ id: "satellite", type: "raster", source: "satellite" }] } : BASEMAPS[state.basemap], { diff: false }); });
  document.getElementById("unselectLayers").addEventListener("click", () => {
    // Use each layer's existing handler to keep visibility, legends and loading state in sync.
    document.querySelectorAll('#layerPanel input[type="checkbox"]:checked').forEach(input => {
      input.checked = false; input.dispatchEvent(new Event('change', { bubbles: true }));
    });
    state.activePopup?.remove();
    refreshMapLoading();
  });
  document.getElementById("resetView").addEventListener("click", resetBrazilView); dom.openInsights.addEventListener("click", () => setDataDrawer(true)); dom.closeInsights.addEventListener("click", () => setDataDrawer(false)); dom.retryMap.addEventListener("click", () => map.setStyle(state.basemap === "satellite" ? map.getStyle() : BASEMAPS[state.basemap], { diff: false })); dom.threeDToggle.addEventListener("click", () => setThreeDimensional(!state.threeDimensional));
  dom.panelCollapse.addEventListener("click", () => setPanelCollapsed(!state.panelCollapsed));
  document.addEventListener("keydown", (event) => { if (event.key === "Escape" && state.summariesOpen) setDataDrawer(false); });
  bindLocationSearch();
}
function primeInitialCensus() { [0, 250, 1200].forEach((delay) => window.setTimeout(() => { ensureCensus(); map.triggerRepaint(); }, delay)); }
function boot() { if (state.booted) return; state.booted = true; social = createSocialIndicators({ map, state, bounds: CHANGE_REGION_BOUNDS, archiveSuffix: SOCIAL_MANIFEST.archiveSuffix, url: pmtilesUrl, popupNode, refresh: refreshMapLoading, closePopup: () => state.activePopup?.remove(), onFirstTile: startOpeningFlight }); createIcons({ icons: { RotateCcw, ContactRound, Grid: Grid2X2, Blocks, Building2, Wallet, BookOpen, Droplets, Info, Network, Trash2, UserRound, UsersRound, Waves, ChartNoAxesCombined, ChevronLeft, ChevronRight, Hexagon, House, Landmark, Leaf, Map: MapIcon, MapPin, Route, Search, TrendingUp } }); restorePanelCollapsed(); bindControls(); document.getElementById("obrasToggle").checked = true; dom.favelasToggle.checked = true; dom.locationSearchInput.value = "Rio de Janeiro"; dom.censusToggle.checked = false; document.querySelector("[data-layer-card='census'] .census-settings").hidden = true; bindFeaturePicking(); bindScrollContainment(); renderLegends(); mountThreeDimensionalControl(); renderThreeDimensionalToggle(); syncEmptyMapHint(); rehydrateMap(); primeInitialCensus(); refreshMapLoading(); window.requestAnimationFrame(collapseAttribution);  }
map.on("load", () => { boot(); social?.recover(); });
map.on("style.load", () => { if (!state.booted) boot(); else { rehydrateMap(); window.requestAnimationFrame(collapseAttribution); } });
map.on("zoom", () => { updateZoomNotice(); ensureCensus(); ensureChange(); });
map.on("zoomend", () => { ensureCensus(); ensureChange(); });
map.on("pitch", updatePopupElevation);
map.on("pitchend", () => { state.threeDimensional = map.getPitch() >= 20; renderThreeDimensionalToggle(); });
map.on("sourcedata", (event) => {
  if (!event.sourceId) return;
  const censusSource = state.censusSources.get(event.sourceId);
  // CONTRACT: PMTiles source registration can occur before its first range
  // request. The first tile-content event, rather than global source idleness,
  // proves that this tier is available to draw at the visitor's location.
  if (censusSource && event.sourceDataType === "content") { clearCensusTimer(event.sourceId); state.censusAttempts.delete(event.sourceId); state.censusSources.set(event.sourceId, { ...censusSource, status: "ready" }); syncCensusVisibility(); return; }
  const changeSource = state.changeSources.get(event.sourceId);
  if (changeSource && event.sourceDataType === "content") { clearChangeTimer(event.sourceId); state.changeAttempts.delete(event.sourceId); state.changeSources.set(event.sourceId, { ...changeSource, status: "ready" }); syncChangeVisibility(); return; }
  const projectSource = state.projectSources.get(event.sourceId);
  if (projectSource && event.sourceDataType === "content") { clearProjectTimer(event.sourceId); state.projectAttempts.delete(event.sourceId); state.projectSources.set(event.sourceId, { ...projectSource, status: "ready", timer: null }); refreshMapLoading(); }
});
map.on("sourcedataloading", (event) => {
  if (!event.sourceId || !sourceIsSelected(event.sourceId)) return;
  state.mapTilesLoading = true;
  refreshMapLoading();
});
map.on("idle", () => {
  state.mapTilesLoading = false;
  refreshMapLoading();
});
map.on("moveend", () => { ensureCensus(); ensureChange(); refreshMapLoading(); });
map.on("error", (event) => {
  const censusSource = event.sourceId && state.censusSources.get(event.sourceId);
  if (censusSource) {
    if (censusSource.retryQueued) return;
    state.censusSources.set(event.sourceId, { ...censusSource, retryQueued: true });
    window.setTimeout(() => retryCensusLevel(censusSource.year, censusSource.definition.level, "error"), 400);
    return;
  }
  const changeSource = event.sourceId && state.changeSources.get(event.sourceId);
  if (changeSource) {
    if (changeSource.retryQueued) return;
    state.changeSources.set(event.sourceId, { ...changeSource, retryQueued: true });
    window.setTimeout(() => retryChangeSource(changeSource.definition), 400);
    return;
  }
  if (event.sourceId && state.projectSources.has(event.sourceId)) { const projectSource = state.projectSources.get(event.sourceId); if (!projectSource.retryQueued) { state.projectSources.set(event.sourceId, { ...projectSource, retryQueued: true }); window.setTimeout(() => retryProjectSource(event.sourceId, "error"), 400); } }
  console.error(event.error);
});
updateZoomNotice();

// Allow retry even when the external basemap style has not finished loading.
const startupWatchdog=setTimeout(()=>{if(!state.booted)setLoading("Basemap is taking longer than expected. Retry if needed.",true);},15000);
map.once('style.load',()=>clearTimeout(startupWatchdog));
dom.retryMap.addEventListener('click',()=>{if(!state.booted){setLoading('Retrying basemap…');map.setStyle(BASEMAPS[state.basemap],{diff:false});}});
window.addEventListener('online',()=>{if(!state.booted)map.setStyle(BASEMAPS[state.basemap],{diff:false});else social?.recover();});
