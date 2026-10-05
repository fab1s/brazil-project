#note/project 

> [!WARNING]
> Some data access is restricted to Brazil; users outside the country may need to connect via a Brazil VPN.


## 1 IBGE Census Data

| Nr. | **Data**                                          | Type                     | Source | Format    | Years            | Access                                                                                      |
| --- | ------------------------------------------------- | ------------------------ | ------ | --------- | ---------------- | ------------------------------------------------------------------------------------------- |
| 1.1 | **Census tract-level aggregate data.**            | Statistical dataset      | IBGE   | dataframe | 2000, 2010, 2022 | [censobr](https://github.com/ipea/censobr)                                                  |
| 1.2 | **Sample microdata (Microdados da amostra)**      | Anonymised microdata     | IBGE   | dataframe | 2000, 2010       | [censobr](https://github.com/ipea/censobr)                                                  |
| 1.3 | **Census weighting area (área de ponderação)**    | Boundary dataset         | IBGE   | .shp      | 2010, 2022       | [geobr](https://github.com/ipea/geobr) (2010), ?(2000/2022)                                 |
| 1.4 | **Census tract shape file (Setores censitários)** | Boundary dataset         | IBGE   | .shp      | 2000, 2010, 2022 | [geobr](https://github.com/ipea/geobr)                                                      |
| 1.5 | **Sala de Acesso a Dados Restritos**              | Non-anonymised microdata | IBGE   |           |                  | [gov.br](https://www.gov.br/pt-br/servicos/solicitacao-de-acesso-a-sala-de-dados-restritos) |

### 1.1 Census tract-level aggregate data
- Smallest territorial unit

The aggregate data at the census tract level is collected through two questionnaires. The *resultados do universo* (universe results) combines responses to the variables common to both the **basic questionnaire** (questionário básico) and the **sample questionnaire** (questionário da amostra) across all households, delivering complete coverage. The sample questionnaire covers additional social, economic, and demographic variables collected only from a sampled fraction of households: 20% in municipalities up to 15,000 inhabitants and 10% in larger ones (IBGE, 2003, p. 7).

> [!warning] Issues
> - ~~Microdata from the sample questionnaire available, but only for weighted areas which are not available for the 2000 census.~~
> 	- IBGE has reported that it is possible to create the weighted area of the year 2000 with the available data. Will look into it depending on need. 
> - "Universe result" for the 2000 census does not contain racial data, only as sample data (microdata)
### 1.2 Sample microdata (microdados da amostra)
- Anonymised individual-level records from the sample questionnaire
    - Finest geographic identifier: área de ponderação (weighting area) level (not census tract)
- Available for 1960, 1970, 1980, 1991, 2000 & 2010
	- 2022 micro-data not released, yet?!


**Table 1: Overview of IBGE Census variable availability by questionnaire type and year for the person tables** 

| Variable                        | B 2000 | S 2000 | B 2010 | B 2022 | S 2010 | S 2022 |
| ------------------------------- | :----: | :----: | :----: | :----: | :----: | :----: |
| **Demographics**                |        |        |        |        |        |        |
| Sex                             |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |
| Age / date of birth             |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |
| Household relationship          |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |
| **Race & ethnicity**            |        |        |        |        |        |        |
| Race / color                    |   —    |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |
| Indigenous identification       |   —    |   —    |   ✓    |   ✓    |   ✓    |   ✓    |
| Indigenous ethnicity            |   —    |   —    |   ✓    |   ✓    |   ✓    |   ✓    |
| Indigenous language             |   —    |   —    |   ✓    |   ✓    |   ✓    |   ✓    |
| Quilombola identification       |   —    |   —    |   —    |   ✓    |   —    |   ✓    |
| **Education**                   |        |        |        |        |        |        |
| Literacy                        |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |
| Educational attainment          |   —    |   ✓    |   —    |   —    |   ✓    |   ✓    |
| Grade completed                 |   ✓*   |   ✓    |   —    |   —    |   ✓    |   ✓    |
| **Civil registration & income** |        |        |        |        |        |        |
| Birth registration              |   —    |   —    |   ✓    |   ✓    |   ✓    |   ✓    |
| Individual income               |   —    |   ✓    |   ✓    |   —    |   ✓    |   ✓    |
| Household responsible income    |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |   ✓    |
\*Last completed grade (*ensino fundamental only*), household responsible only

**Documents**
- [Questionnaires & code books](https://lunduniversityo365-my.sharepoint.com/:f:/r/personal/fa4850sc_lu_se/Documents/Brazil%20Project/Scripts_Data/IBGE/Questionairs%20and%20Codebooks?d=w85a4697ab2c549279c606196ec910ec9&csf=1&web=1&e=9IFbTM)
---
### 1.3 Census weighting area (área de ponderação)
- Smallest unit with statistical representativeness from sample data (anonymised microdata)
- Purpose: calibration of sample weights
- Minimum 400 occupied households (2010 census)

> [!warning] Issues
> - Not found for ~~2000 and~~ 2022, **only for 2010**
> 	- 2000 apparently available but labour intensive (see data [[pedido_11118204.pdf|request]])
> 	- 2010 available over [geobr](https://github.com/ipea/geobr)


### 1.4 Census tract shape file



Unavailable:
- 2022 not out yet (as of 2026-07-27)
### 1.5 Sala de Acesso a Dados Restritos 
- Non-anonymised microdata
- Access requirements ([gov.br](https://www.gov.br/pt-br/servicos/solicitacao-de-acesso-a-sala-de-dados-restritos)):
	- On-site only (IBGE HQ, Rio de Janeiro)
    - Institutional affiliation
    - Research project approved by IBGE committee (*Comitê de Avaliação de Acesso a Dados não Desidentificados*)
- Outputs reviewed by IBGE before release to prevent re-identification

## 2 Land value data

### 2.1 Belo Horizonte

| **Data**                                     | Type             | Source   | Format                         | Years                         | Access                                                                                    |
| -------------------------------------------- | ---------------- | -------- | ------------------------------ | ----------------------------- | ----------------------------------------------------------------------------------------- |
| **Zona Homogênea** (Homogeneous Zone)        | Boundary dataset | PRODABEL | Georeferenced CSV (EPSG:31983) | June 2022 - present (monthly) | [Dados abertos - BH](https://dados.pbh.gov.br/dataset/zona-homogenea-iptu)                |
| **Cadastro Imobiliário** (Property Registry) | Boundary dataset | PRODABEL | Georeferenced CSV (EPSG:31983) | June 2022 - present (monthly) | [Dados abertos - BH](https://ckan.pbh.gov.br/organization/smfa?tags=cadastro+imobiliário) |

- Planta genérica de valores (PGV, [source](https://www.jusbrasil.com.br/artigos/planta-generica-de-valores-o-que-e-para-que-serve-qual-a-sua-importancia/5477982036))
	- Data used by municipalities to fix the unitary square meter values of land and construction
	- Standard reference values for real estate, based on location,  square footage, finish and use
	- Used as basis of calculation for the IPTU (Property Tax)
- [Zona Homogênea IPTU](https://dados.pbh.gov.br/dataset/zona-homogenea-iptu) 
	- Spatial object, updated monthly
	- Grouped areas with similar real-estate market values
	- Used as a spatial unit in the *IPTU* valuation system
	- Helps determine a property’s *valor venal* (assessed value) for tax purposes
- [Cadastro Imobiliário Regional](https://ckan.pbh.gov.br/organization/smfa?tags=belo+horizonte)
	- Available per neighbourhood 
	- Spatial dataset of all active properties in Belo Horizonte.
	- Contains parcel-level cadastral and building characteristics.
	- Linked to the municipality’s **Zona Homogênea (ZH)** valuation system.
	- Includes georeferenced property records
- Valor venal
	- official government-assessed value of an asset
	- [Calculation](https://fazenda.pbh.gov.br/internet/legislacao/formchave.asp?key=295)

> [!Note] Overal note
> - The square meter value for Belo Horizonte are contained in the Annexes of Law No.     [9,795/2009](https://leis.org/municipais/mg/belo-horizonte/lei/lei-ordinaria/2009/9795/lei-ordinaria-n-9795-2009-altera-a-politica-tributaria-do-imposto-sobre-a-propriedade-predial-e-territorial-urbana-iptu-e-da-outras-providencias)
> 	- Apparently these are reference tables that do not periodically update, but might be amended
> 	- In 2014, valor venal values were updated by IPCA-E inflation ([DECRETO Nº 15.433](https://leis.org/municipais/mg/belo-horizonte/lei/decreto/2013/15433/decreto-n-15433-2013-regulamenta-a-notificacao-a-concessao-de-beneficios-e-o-recolhimento-do-imposto-sobre-a-propriedade-predial-e-territorial-urbana-iptu-do-exercicio-de-2014-da-taxa-de-coleta-de-residuos-solidos-urbanos-tcr-da-taxa-de-fiscalizacao-de-aparelhos-de-transporte-tfat-e-da-contribuicao-para-o-custeio-dos-servicos-de-iluminacao-publica-ccip-que-com-ele-sao))

## 3 Spatial harmonisation

### 3.1 IBGE Data 
[Harmonizing income classes from 2000 and 2010 Brazilian censuses](zotero://open-pdf/library/items/5X2Y6A5M)
- Real income adjustment for spatio-temporal comparison

## 4 Mega projects

Access project map: https://sandy-ivory-k65c.here.now

**Potential sources**

| Nr  | Database        | Organization                                                        | Data Type                                                 | Coverage                                                                | Access                                                                                                                                                                                                                                                                                              |
| --- | --------------- | ------------------------------------------------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 4.1 | INDE            | National Spatial Data Infrastructure                                |                                                           |                                                                         | [INDE](https://inde.gov.br/CatalogoGeoservicos)                                                                                                                                                                                                                                                     |
| 4.2 | IBAMA           | Brazilian Institute of Environment and Renewable Natural Resources  | Environmental licensing files                             | Multi-sector projects requiring environmental permits                   | [SISLIC (IBAMA)](https://servicos.ibama.gov.br/licenciamento/consulta_empreendimentos.php), [Basic data](https://dadosabertos.ibama.gov.br/dataset/licencas-ambientais-de-atividades-e-empreendimentos-licenciados-pelo-ibama), [GeoData](https://pamgia.ibama.gov.br/server/rest/services/SIGAGEO) |
| 4.3 | PAC             | Growth Acceleration Program (Programa de Aceleração do Crescimento) | Investment records                                        | Government infrastructure investments                                   |                                                                                                                                                                                                                                                                                                     |
| 4.4 | Obrasgov (CIPI) |                                                                     | Federal infrastructure project records                    | Projects funded wholly or partly by Brazil's federal budget             | [obragovr](https://strategicprojects.github.io/obrasgovr/), [CIPI's Swagger UI](https://cipi.economia.gov.br/cipi-backend/swagger-ui.html)                                                                                                                                                          |
|     | ANEEL           | National Electric Energy Agency                                     | Energy project databases                                  | Energy sector infrastructure                                            |                                                                                                                                                                                                                                                                                                     |
|     | ANTT            | Agência Nacional de Transportes Terrestres                          | Land transportation infrastructure, routes, and services  | Highway networks, logistics corridors, terrestrial transport regulation | [GeoData](https://dados.antt.gov.br/group/rodovias)                                                                                                                                                                                                                                                 |
|     | EPE             | Empresa de Pesquisa Energética                                      | Energy sector research, strategic planning, and forecasts | National energy planning, generation capacity, demand forecasting       |                                                                                                                                                                                                                                                                                                     |
|     | ONS             | Operador Nacional do Sistema Elétrico                               | Electricity generation, transmission, and grid data       | Power grid operations, energy distribution, real time grid management   |                                                                                                                                                                                                                                                                                                     |
|     | MME             | Ministério de Minas e Energia                                       | Energy policy, mining regulations, and sector data        | Energy infrastructure projects, mining operations, sector policy        |                                                                                                                                                                                                                                                                                                     |

### 4.1 INDE
**What is it?** Brazil's National Spatial Data Infrastructure for cataloging and sharing government geospatial data.

- IBAMA: **not available**
	- Source: [INDE - IBAMA](https://metadados.inde.gov.br/geonetwork/srv/por/catalog.search;jsessionid=47D4ED21C9CC628A5230C8F109F96215#/search?facet.q=category%2FIBAMA&resultType=details&sortBy=relevance&fast=index&_content_type=json&from=101&to=200&any=Licenciamento)
	- 
### 4.2 IBAMA

> [!Summary] To the point
> - Environmental data available at **[Pamgia - GeoData](https://pamgia.ibama.gov.br/server/rest/services/SIGAGEO)**

The system of environmental licensing (*Sistema de Licenciamento Ambiental* - SISLIC) contains the environmental licensing files covering the energy, transport & infrastructure, transmission & distribution, extraction and other categories. Each project is coded by the stages of environmental licensing from initial assessment through operation.

- [SISLIC](https://servicos.ibama.gov.br/licenciamento/consulta_empreendimentos.php) contains documentation in three levels:
	1. **Summary record** (structured): Basic project description, with attributes such as
		- Infrastructure type,
	    - coordinates,
	    - municipality,
	    - developer,
	    - licensing status,
	    - technical specifications,
	    - affected Indigenous lands,
	    - associated infrastructure,
	    - environmental studies.
	2. **Process information**: Detailed timeline of licensing stages with dates
	3. **Document collection**: Various types of process document
- Basic attributes are also available under [dadosabertos.ibama.gov.br](https://dadosabertos.ibama.gov.br/dataset/licencas-ambientais-de-atividades-e-empreendimentos-licenciados-pelo-ibama)

**Other sources**
- [Pamgia](https://pamgia.ibama.gov.br/repositorio-de-dados/?group=Energia) from IBAMA contains geodata at a limited extend, not sure how it relates to [environmental licenses](https://servicos.ibama.gov.br/licenciamento/consulta_empreendimentos.php)
- **GeoData**: Extensive [Pamgia - GeoData](https://pamgia.ibama.gov.br/server/rest/services/SIGAGEO) for environmental licences processed through the API-Transactional (SERPRO)
	- Not sure when data get updated
	
	GeoData from environmental licenses:
	- [tb_empreendimento_repr_p](https://pamgia.ibama.gov.br/server/rest/services/SIGAGEO/tb_empreendimento_repr_p/FeatureServer): ==point== geometries 
	- [tb_empreendimento_repr_l](https://pamgia.ibama.gov.br/server/rest/services/SIGAGEO/tb_empreendimento_repr_l/FeatureServer): ==line== geometries
	- [tb_empreendimento_repr_a](https://pamgia.ibama.gov.br/server/rest/services/SIGAGEO/tb_empreendimento_repr_a/FeatureServer): ==polygon and multipolygon== geometries
### 4.3 PAC

- GeoPAC is an Embrapa geospatial system tracking Brazil's PAC projects
	- [Technical report](https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/981235/1/20140225-GeoPAC2.pdf)
	- 

### 4.4 Obrasgov (CIPI)
**What is it?** An initiative to bring transparency to federally funded projects, contains an extensive list of mainly federally funded projects nationwide (small, big and mega).

> [!Summary] To the point
> - API available through [obragovr](https://strategicprojects.github.io/obrasgovr/) (metadata and point geometries) and [CIPI’s Swagger UI](https://cipi.economia.gov.br/cipi-backend/swagger-ui.html) to extract geometries beyond points.

- User manual: [Manual do Usuário - Obrasgov.br](zotero://open-pdf/library/items/PEXXU8FX)

## Tessera

Sources:
- [Tessera website](https://geotessera.org)
- Python Library: [GeoTessera](https://pypi.org/project/geotessera/)

```Text
Using country 'Brazil': [73.987235°W, 33.768378°S] - [34.729993°W, 5.244486°N]
Exporting all 128 bands
 Format:          TIFF 
 Year:            2024 
 Compression:     lzw  
 Dataset version: v1   
Found 110630 tiles for region in year 2024
 Files to download:   110,630 
 Total download size: 61.5 TB 
 Tiles in region:     110,630 
 Year:                2024    
 Format:              TIFF    
Note: TIFF sizes are estimates (4x quantized size)
```