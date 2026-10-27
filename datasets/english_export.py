"""Present preserved geographic records with English field names and reviewed labels.

The source GeoPackages remain immutable. SQLite schema edits are applied only to a
checked copy, so feature IDs and geometry blobs are never decoded or rewritten.
"""

import json
import hashlib
import re
from pathlib import Path
import shutil
import sqlite3


COMMUNITIES = {
    "cd_fcu": "community_code",
    "nm_fcu": "community_name",
    "cd_uf": "state_code",
    "nm_uf": "state_name",
    "sigla_uf": "state_abbreviation",
    "cd_mun": "municipality_code",
    "nm_mun": "municipality_name",
}

IBAMA = {
    "objectid": "record_id",
    "tp_elemento": "element_type_original",
    "no_empreendimento": "project_name_original",
    "tp_setor": "sector_original",
    "tp_tipologia": "project_type_original",
    "nu_sei_formatado": "sei_case_number",
    "url_licencas_emitidas": "issued_licenses_url",
    "sei_no_empreendimento": "sei_project_name_original",
    "licencas": "licenses_original",
    "no_empreendedor": "developer_name_original",
    "tp_sector_en": "sector_english",
}

OBRASGOV = {
    "declared_uf": "declared_state",
    "id_projeto_investimento": "investment_project_id",
    "projeto_estruturante": "strategic_project_original",
    "desc_nome": "project_name_original",
    "nr_cep": "postal_code",
    "desc_endereco": "address_original",
    "desc_projeto": "project_description_original",
    "desc_funcao_social": "social_purpose_original",
    "desc_meta_global": "overall_goal_original",
    "dt_inicial_prevista": "planned_start_date",
    "dt_final_prevista": "planned_end_date",
    "dt_cadastro": "registration_date",
    "ano_cadastro": "registration_year",
    "natureza_intervencao": "intervention_nature_original",
    "id_natureza_intervencao": "intervention_nature_id",
    "especie_intervencao": "intervention_kind_original",
    "id_especie_intervencao": "intervention_kind_id",
    "situacao": "project_status_original",
    "uf_principal": "primary_state",
    "organizacao_resp": "responsible_organisation_original",
    "cnpj_organizacao_resp": "responsible_organisation_cnpj",
    "populacao_beneficiada": "beneficiary_population",
    "desc_populacao_beneficiada": "beneficiary_description_original",
    "qtd_empregos_gerados": "jobs_created",
    "ind_bim": "bim_indicator",
    "dt_inicial_efetiva": "actual_start_date",
    "dt_final_efetiva": "actual_end_date",
    "obs_pertinentes_intervencao": "intervention_notes_original",
    "sistema_resp": "responsible_system",
    "possui_estudo_viabilidade": "has_feasibility_study_original",
    "eixo": "policy_axis_original",
    "id_eixo": "policy_axis_id",
    "tipo": "project_type_original",
    "id_tipo": "project_type_id",
    "subtipo": "project_subtype_original",
    "id_subtipo": "project_subtype_id",
    "vl_investimento_previsto_total": "planned_total_investment_brl",
}

IBAMA_CATEGORIES = {
    "sector": {
        "Transporte": "Transportation", "Energia": "Energy",
        "Mineração": "Mining", "Petróleo e Gás": "Oil and Gas",
        "Outros": "Other", "Recursos Hídricos": "Water Resources",
        "Nuclear/Radiativa": "Nuclear/Radioactive",
    },
    "element_type": {
        "Área de Porto": "Port area", "Área de Terminal": "Terminal area",
        "Barramento": "Dam structure", "Área de Estudo": "Study area",
        "Estrutura pontual": "Point structure", "Trecho Rodoviário": "Road segment",
        "Ponte Rodoviária": "Road bridge", "Trecho Ferroviário": "Rail segment",
        "Ponte Ferroviária": "Rail bridge", "Trecho Hidroviário": "Waterway segment",
        "Trecho de Duto": "Pipeline segment", "Trecho de Energia": "Energy corridor segment",
        "Trecho de Vazão Reduzida": "Reduced-flow segment",
        "Estrutura linear": "Linear structure", "Área de Dragagem": "Dredging area",
        "Reservatório de Hidrelétrica": "Hydroelectric reservoir",
        "Área do Empreendimento": "Project area",
        "Área de Aquisição de Dados": "Data acquisition area",
        "Área de outros métodos de aquisição": "Other data-acquisition area",
        "Área de Perfuração": "Drilling area",
        "Sistema de Produção": "Production system",
        "Reservatório de Hidrelétrica e Barramentos": "Hydroelectric reservoir and dams",
    },
    "project_type": {
        "Transporte Hidroviário Marítimo": "Maritime water transport",
        "Usina hidrelétrica": "Hydroelectric plant",
        "Central de geração hidrelétrica": "Hydroelectric generation facility",
        "Pequena central hidrelétrica": "Small hydroelectric plant",
        "Usina eólica": "Wind farm", "Usina eólica offshore": "Offshore wind farm",
        "Mineração": "Mining", "Petróleo e Gás - Onshore": "Oil and gas - onshore",
        "Carcinicultura": "Shrimp farming", "Complexo Turístico": "Tourism complex",
        "Empreendimento Agropecuário": "Agricultural or livestock project",
        "Posto de Abastecimento": "Fuel station",
        "Sistema de Abastecimento de Água": "Water supply system",
        "Sistema de Esgotamento Sanitário": "Sewerage system",
        "Aeroporto": "Airport", "Aterro Sanitário": "Sanitary landfill",
        "Antenas": "Antennas", "Irrigação": "Irrigation",
        "Base Aeroespacial": "Aerospace base",
        "Instalação Nuclear/Radiativa": "Nuclear or radioactive facility",
        "Estruturas Rodoviárias": "Road infrastructure",
        "Estruturas Ferroviárias": "Rail infrastructure",
        "Transporte Hidroviário Fluvial": "River transport",
        "Duto terrestre": "Land pipeline",
        "Sistema de transmissão": "Electricity transmission system",
        "Sistema de distribuição": "Electricity distribution system",
        "Transposição": "Water transfer", "Cabo Óptico": "Optical cable",
        "Petróleo e Gás - Aquisição": "Oil and gas - data acquisition",
        "Petróleo e Gás - Perfuração": "Oil and gas - drilling",
        "Petróleo e Gás - Produção": "Oil and gas - production",
    },
}

OBRASGOV_CATEGORIES = {
    "strategic_project": {"SIM": "Yes", "NÃO": "No"},
    "intervention_nature": {
        "Obra": "Construction work", "Outros": "Other", "Projeto": "Project",
        "Estudo": "Study", "Projeto de Investimento em Infraestrutura": "Infrastructure investment project",
    },
    "intervention_kind": {
        "Reforma": "Renovation", "Construção": "Construction",
        "Ampliação": "Expansion", "Fabricação": "Manufacturing",
        "Recuperação": "Rehabilitation", "Máquinas e Equipamentos": "Machinery and equipment",
    },
    "project_status": {
        "Concluída": "Completed", "Cadastrada": "Registered",
        "Em execução": "In progress", "Cancelada": "Cancelled",
        "Inacabada": "Unfinished", "Paralisada": "Halted",
    },
    "has_feasibility_study": {"SIM": "Yes", "NÃO": "No"},
    "policy_axis": {
        "Econômico": "Economic", "Social": "Social",
        "Administrativo": "Administrative", "Militar": "Military",
    },
}


LICENSE_TERMS = {
    "Anuência": "Consent", "Autorização": "Authorisation",
    "Autorização de Operação": "Operating authorisation",
    "Indeferimento de Licença de Instalação": "Denial of installation licence",
    "Licença Prévia": "Preliminary licence",
    "Licença de Instalação": "Installation licence",
    "Licença de Operação": "Operating licence",
    "Licença de Pesquisa Sísmica": "Seismic survey licence",
    "Renovação de Licença de Instalação": "Renewal of installation licence",
    "Renovação de Licença de Pesquisa Sísmica": "Renewal of seismic survey licence",
    "Retificação da Licença de Pesquisa Sísmica": "Amendment of seismic survey licence",
    "Retificação da Renovação de Licença de Instalação": "Amendment of installation-licence renewal",
    "Retificação da Renovação de Licença de Pesquisa Sísmica": "Amendment of seismic-survey-licence renewal",
    "Retificação de Autorização": "Amendment of authorisation",
    "Retificação de Licença Prévia": "Amendment of preliminary licence",
    "Retificação de Licença de Instalação": "Amendment of installation licence",
    "Retificação de Licença de Operação": "Amendment of operating licence",
}


def _quote(name):
    return '"' + name.replace('"', '""') + '"'


def _data_columns(connection, layer):
    return [row[1] for row in connection.execute(f"PRAGMA table_info({_quote(layer)})")]


def _add_english_values(connection, layer, field, translations):
    original = field + "_original"
    english = field + "_english"
    actual = {value for (value,) in connection.execute(
        f"SELECT DISTINCT {_quote(original)} FROM {_quote(layer)} WHERE {_quote(original)} IS NOT NULL")}
    missing = actual - translations.keys()
    if missing:
        raise ValueError(f"{layer}.{original}: unmapped labels: {sorted(missing)[:12]}")
    connection.execute(f"ALTER TABLE {_quote(layer)} ADD COLUMN {_quote(english)} TEXT")
    connection.execute("CREATE TEMP TABLE label_translation(original TEXT PRIMARY KEY, english TEXT NOT NULL)")
    connection.executemany("INSERT INTO label_translation VALUES (?, ?)", translations.items())
    connection.execute(f"UPDATE {_quote(layer)} SET {_quote(english)}="
                       f"(SELECT english FROM label_translation WHERE original={_quote(original)}) "
                       f"WHERE {_quote(original)} IS NOT NULL")
    connection.execute("DROP TABLE label_translation")
    return english


def _translate_licenses(value):
    if value is None:
        return None
    translated = value
    for original, english in sorted(LICENSE_TERMS.items(), key=lambda item: -len(item[0])):
        translated = translated.replace("(" + original + "-", "(" + english + "-")
    return translated


def _add_dictionary(connection, rows, source_sha, code_sha, translations_sha):
    connection.execute("CREATE TABLE field_dictionary (source_field TEXT NOT NULL, "
                       "original_value_column TEXT NOT NULL, english_value_column TEXT, "
                       "value_policy TEXT NOT NULL)")
    connection.executemany("INSERT INTO field_dictionary VALUES (?,?,?,?)", rows)
    connection.execute("CREATE TABLE export_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    connection.executemany("INSERT INTO export_metadata VALUES (?,?)", [
        ("source_sha256", source_sha),
        ("schema_policy", "english-fields-original-values-v1"),
        ("export_code_sha256", code_sha),
        ("translation_tables_sha256", translations_sha),
        ("translation_note", "Reviewed category translations; original provider text remains alongside English values."),
    ])
    for name in ("field_dictionary", "export_metadata"):
        connection.execute("INSERT INTO gpkg_contents (table_name,data_type,identifier,description,last_change,srs_id) "
                           "VALUES (?,'attributes',?,?,strftime('%Y-%m-%dT%H:%M:%fZ','now'),NULL)",
                           (name, name, "English export provenance"))


def _category_maps(dataset):
    categories = {"communities": {}, "ibama": IBAMA_CATEGORIES,
                  "obrasgov": OBRASGOV_CATEGORIES}[dataset].copy()
    if dataset == "obrasgov":
        stored = json.loads((Path(__file__).parent / "shared/config/obrasgov_translations.json").read_text())
        categories.update({"project_type": stored["type"],
                           "project_subtype": stored["subtype"]})
    return categories


def _category_hash(dataset):
    return hashlib.sha256(json.dumps(_category_maps(dataset), sort_keys=True,
                                     ensure_ascii=False).encode()).hexdigest()


def export(source, target, dataset, source_sha):
    """Copy a verified producer, rename fields, add translations, then publish later."""
    source, target = Path(source), Path(target)
    if target.exists():
        raise FileExistsError(target)
    shutil.copyfile(source, target)
    try:
        with sqlite3.connect(target) as connection:
            # GeoPackage RTree triggers reference GDAL functions even for
            # attribute-only UPDATEs. They must never run on this export.
            def geometry_mutation(*_args):
                raise ValueError("English export attempted a geometry or feature-ID edit")
            for function in ("ST_IsEmpty", "ST_MinX", "ST_MaxX", "ST_MinY", "ST_MaxY"):
                connection.create_function(function, 1, geometry_mutation)
            layers = {"communities": ("favelas_2022",),
                      "ibama": ("licensed_projects_st",),
                      "obrasgov": ("map_components", "excluded_primary_state")}[dataset]
            fields = {"communities": COMMUNITIES, "ibama": IBAMA,
                      "obrasgov": OBRASGOV}[dataset]
            categories = _category_maps(dataset)
            rows = []
            for layer in layers:
                existing = set(_data_columns(connection, layer))
                if not set(fields).issubset(existing):
                    raise ValueError(f"{layer}: missing original provider fields: {set(fields) - existing}")
                if dataset == "ibama":
                    # The source already carries a reviewed sector translation.
                    original_sectors = dict(connection.execute(
                        f"SELECT DISTINCT tp_setor, tp_sector_en FROM {_quote(layer)}"))
                    if original_sectors != IBAMA_CATEGORIES["sector"]:
                        raise ValueError("IBAMA's saved English sectors differ from the reviewed map")
                for old, new in fields.items():
                    connection.execute(f"ALTER TABLE {_quote(layer)} RENAME COLUMN {_quote(old)} TO {_quote(new)}")
                for old, new in fields.items():
                    base = new.removesuffix("_original")
                    english = None
                    policy = "original value, English field name"
                    if base in categories and not (dataset == "ibama" and base == "sector"):
                        english = _add_english_values(connection, layer, base, categories[base])
                        policy = "reviewed category translation"
                    elif dataset == "ibama" and new == "sector_original":
                        english = "sector_english"
                        policy = "reviewed category translation in preserved source"
                    elif new.endswith("_original"):
                        policy = "original text or proper name; see translation scope"
                    if layer == layers[0]:
                        rows.append((old, new, english, policy))
                if dataset == "ibama":
                    connection.create_function("translate_licenses", 1, _translate_licenses)
                    connection.execute(f"ALTER TABLE {_quote(layer)} ADD COLUMN licenses_english TEXT")
                    connection.execute(f"UPDATE {_quote(layer)} SET licenses_english="
                                       "translate_licenses(licenses_original) WHERE licenses_original IS NOT NULL")
                    observed = {label for (value,) in connection.execute(
                        "SELECT DISTINCT licenses_original FROM licensed_projects_st")
                        if value for label in re.findall(r"\d+-\(([^-]+)-", value)}
                    if observed - LICENSE_TERMS.keys():
                        raise ValueError("Untranslated IBAMA licence terms: "
                                         + str(sorted(observed - LICENSE_TERMS.keys())))
                    rows = [(a, b, "licenses_english" if b == "licenses_original" else c,
                             "reviewed licence-label translation" if b == "licenses_original" else d)
                            for a, b, c, d in rows]
            translations_sha = _category_hash(dataset)
            code_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            _add_dictionary(connection, rows, source_sha, code_sha, translations_sha)
            if connection.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise ValueError("English GeoPackage integrity check failed")
    except BaseException:
        target.unlink(missing_ok=True)
        raise


def verify_export(source, target, dataset, source_sha):
    """Check provenance, every original attribute, feature ID, and geometry blob."""
    layers = {"communities": ("favelas_2022",),
              "ibama": ("licensed_projects_st",),
              "obrasgov": ("map_components", "excluded_primary_state")}[dataset]
    with sqlite3.connect(f"file:{Path(target).resolve()}?mode=ro", uri=True) as connection:
        metadata = dict(connection.execute("SELECT key,value FROM export_metadata"))
        if metadata.get("source_sha256") != source_sha:
            raise ValueError(f"{dataset}: English export is from a different source")
        code_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        if metadata.get("export_code_sha256") != code_sha:
            raise ValueError(f"{dataset}: English export code changed; rebuild the file")
        if metadata.get("translation_tables_sha256") != _category_hash(dataset):
            raise ValueError(f"{dataset}: English translation labels changed; rebuild the file")
        mapping = dict(connection.execute("SELECT source_field,original_value_column FROM field_dictionary"))
        connection.execute("ATTACH DATABASE ? AS original",
                           (f"file:{Path(source).resolve()}?mode=ro",))
        for layer in layers:
            source_columns = [row[1] for row in connection.execute(
                f"PRAGMA original.table_info({_quote(layer)})")]
            comparisons = [f"a.{_quote(mapping.get(column, column))} IS NOT b.{_quote(column)}"
                           for column in source_columns if column != "fid"]
            changed = connection.execute(
                f"SELECT COUNT(*) FROM main.{_quote(layer)} a "
                f"LEFT JOIN original.{_quote(layer)} b ON a.fid=b.fid "
                f"WHERE b.fid IS NULL OR {' OR '.join(comparisons)}").fetchone()[0]
            original_count = connection.execute(
                f"SELECT COUNT(*) FROM original.{_quote(layer)}").fetchone()[0]
            exported_count = connection.execute(
                f"SELECT COUNT(*) FROM main.{_quote(layer)}").fetchone()[0]
            if changed or original_count != exported_count:
                raise ValueError(f"{dataset}.{layer}: original IDs, values, or geometry changed")
            for field, labels in _category_maps(dataset).items():
                if dataset == "ibama" and field == "sector":
                    original_field, english_field = "sector_original", "sector_english"
                else:
                    original_field, english_field = field + "_original", field + "_english"
                observed = dict(connection.execute(
                    f"SELECT DISTINCT {_quote(original_field)},{_quote(english_field)} "
                    f"FROM main.{_quote(layer)} WHERE {_quote(original_field)} IS NOT NULL"))
                if observed != {key: labels[key] for key in observed}:
                    raise ValueError(f"{dataset}.{layer}: {field} translations differ from reviewed labels")
            if dataset == "ibama":
                for original, english in connection.execute(
                    f"SELECT licenses_original,licenses_english FROM main.{_quote(layer)}"):
                    if english != _translate_licenses(original):
                        raise ValueError("IBAMA licence-label translation changed")
    return True
