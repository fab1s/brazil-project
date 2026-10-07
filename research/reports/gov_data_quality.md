# Government projects and census data: national quality review

## Executive summary

<!-- brazil:cell gov_data_quality_summary
import pandas as pd
from brazil_project.reporting import table, markdown
summary = report_json("gov-data-quality")
attr, loc, census = summary["attributes"], summary["locations"], summary["census"]
coverage = ctx.table("gov-data-quality", "census_annual_coverage")
coverage_2022 = coverage.loc[coverage.year.eq(2022)].set_index("measure")
joint = coverage_2022.loc["joint_fully_observed"]
saved, observed = coverage_2022.loc["race_ratio_available"], coverage_2022.loc["race_ratio_fully_observed"]
threshold = loc["shared_coordinate_threshold"]
shared_pct = 100 * loc["shared_point_projects"] / loc["valid_point_projects"] if loc["valid_point_projects"] else None
shared_text = f"{shared_pct:.2f}%" if shared_pct is not None else "percentage unavailable"
markdown(f"This national review covers **{summary['distinct_projects']:,} government projects** recorded in Obrasgov and "
         + f"**{census['n_common_areas']:,} census areas** made comparable between 2010 and 2022. "
         + "It checks whether these records can support a study of infrastructure distance, income and racial composition.")
markdown("**The immediate priority is checking reported locations and project types before calculating distances.** "
         + "Many projects share exactly the same location. Construction dates are rarely recorded, some planned budgets are extremely small, "
         + "and census information can be incomplete even when an income or racial-composition value is available.")
markdown("These findings identify issues to investigate; they do not prove that the records are wrong or that particular communities have less infrastructure. "
         + "No additional records were removed or corrected in this review.")
markdown("## Main findings")
rows = [
    {"Topic": "Project counts", "Finding": f"{summary['source_rows']:,} entries describe {summary['distinct_projects']:,} different projects; {summary['source_rows'] - summary['distinct_projects']:,} entries repeat a project.",
     "Why it matters": "Some projects appear more than once because they have several classifications. Repeated entries should not count as extra projects."},
    {"Topic": "Reported locations", "Finding": f"{loc['shared_point_projects']:,} of {loc['valid_point_projects']:,} projects with coordinates passing a basic range check ({shared_text}) have a location recorded for at least {threshold} different projects.",
     "Why it matters": "A shared location can be legitimate or a generic address. Confirm the actual site before treating it as infrastructure near residents."},
    {"Topic": "Project types", "Finding": f"{attr['projects_with_category_review']:,} projects combine education-related wording or organisations with a water/ports classification.",
     "Why it matters": "This suggests categories need review; it does not establish that they are wrong."},
    {"Topic": "Construction dates", "Finding": f"Actual starts are recorded for {attr['projects_with_effective_start']:,} projects ({attr['projects_with_effective_start_pct']:.2f}%); actual finishes for {attr['projects_with_effective_finish']:,} ({attr['projects_with_effective_finish_pct']:.2f}%).",
     "Why it matters": "Registration and planned dates cannot establish when construction occurred or a service opened."},
    {"Topic": "Budget amounts", "Finding": f"{attr['projects_with_budget_001']:,} projects ({attr['projects_with_budget_001_pct']:.2f}%) report R$0.01.",
     "Why it matters": "Check these amounts before weighting projects by investment. The recorded budgets are planned amounts, not money confirmed as spent."},
    {"Topic": "Census information, 2022", "Finding": f"{int(joint['n_common_areas']):,} of {census['n_common_areas']:,} areas ({joint['share_pct']:.2f}%) have complete usable inputs for both income and racial composition.",
     "Why it matters": "About one in ten areas has gaps. Excluding them could change who is represented; this check does not remove areas from the study."},
]
table(pd.DataFrame(rows))
markdown("The location count includes points already withheld from the map: passing a coordinate-range check does not confirm an accurate site. "
         + "Census percentages count areas, not people. "
         + f"Review date: {pd.Timestamp(summary['as_of_date']).strftime('%d %B %Y').lstrip('0')}.")
figures = summary["figures"]
for name, heading, explanation, caption in [
    ("location-overview.png", "Many projects share the same recorded location",
     "Large clusters could strongly influence a distance study if each project is treated as a separate nearby site. The records need checking to establish whether these are shared facilities, generic addresses or inaccurate locations.",
     f"Red dots mark locations shared by at least {threshold} different projects. The map includes points already withheld from the project map. It shows recorded locations, not verified infrastructure sites; lines, polygons and missing or invalid points are omitted."),
    ("date-coverage.png", "The records rarely tell us when construction happened",
     "The shortage of actual start and finish dates limits comparisons of neighbourhood conditions before and after a project. Even a reported finish date does not confirm when a service became operational.",
     "Bars show how many distinct projects have each type of date. Registration records when a project entered the system; planned dates describe intentions. Neither substitutes for actual construction or opening dates."),
    ("income-coverage.png", "An available census value can conceal missing information",
     f"In 2022, racial-composition values are available for {saved['share_pct']:.2f}% of areas, but only {observed['share_pct']:.2f}% have all the required population counts. "
     + "The existing calculation can treat a missing count as zero, so an available result does not always mean the underlying information is complete.",
     f"Percentages are calculated across all {census['n_common_areas']:,} areas in each year. The chart separates available results from complete required information. It describes data coverage, not differences in infrastructure proximity."),
]:
    if name not in figures:
        raise RuntimeError("Missing required summary figure: " + name)
    markdown("## " + heading)
    markdown(explanation)
    report_image(figures[name])
    markdown(caption)
markdown("Income here is an area average based on household heads; racial composition describes the residents. "
         + "These measures cannot tell us the income of individual Black or Brown residents or establish why infrastructure is located where it is. "
         + "Distances and regression results are not part of this assessment.")
-->

<!-- brazil:output gov_data_quality_summary begin -->
This national review covers **129,961 government projects** recorded in Obrasgov and **287,178 census areas** made comparable between 2010 and 2022. It checks whether these records can support a study of infrastructure distance, income and racial composition.

**The immediate priority is checking reported locations and project types before calculating distances.** Many projects share exactly the same location. Construction dates are rarely recorded, some planned budgets are extremely small, and census information can be incomplete even when an income or racial-composition value is available.

These findings identify issues to investigate; they do not prove that the records are wrong or that particular communities have less infrastructure. No additional records were removed or corrected in this review.

## Main findings

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Topic</th>
      <th>Finding</th>
      <th>Why it matters</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Project counts</td>
      <td>134,929 entries describe 129,961 different projects; 4,968 entries repeat a project.</td>
      <td>Some projects appear more than once because they have several classifications. Repeated entries should not count as extra projects.</td>
    </tr>
    <tr>
      <td>Reported locations</td>
      <td>27,953 of 127,081 projects with coordinates passing a basic range check (22.00%) have a location recorded for at least 25 different projects.</td>
      <td>A shared location can be legitimate or a generic address. Confirm the actual site before treating it as infrastructure near residents.</td>
    </tr>
    <tr>
      <td>Project types</td>
      <td>25,216 projects combine education-related wording or organisations with a water/ports classification.</td>
      <td>This suggests categories need review; it does not establish that they are wrong.</td>
    </tr>
    <tr>
      <td>Construction dates</td>
      <td>Actual starts are recorded for 1,750 projects (1.35%); actual finishes for 1,241 (0.95%).</td>
      <td>Registration and planned dates cannot establish when construction occurred or a service opened.</td>
    </tr>
    <tr>
      <td>Budget amounts</td>
      <td>20,532 projects (15.80%) report R$0.01.</td>
      <td>Check these amounts before weighting projects by investment. The recorded budgets are planned amounts, not money confirmed as spent.</td>
    </tr>
    <tr>
      <td>Census information, 2022</td>
      <td>256,907 of 287,178 areas (89.46%) have complete usable inputs for both income and racial composition.</td>
      <td>About one in ten areas has gaps. Excluding them could change who is represented; this check does not remove areas from the study.</td>
    </tr>
  </tbody>
</table>

The location count includes points already withheld from the map: passing a coordinate-range check does not confirm an accurate site. Census percentages count areas, not people. Review date: 7 October 2026.

## Many projects share the same recorded location

Large clusters could strongly influence a distance study if each project is treated as a separate nearby site. The records need checking to establish whether these are shared facilities, generic addresses or inaccurate locations.

![Generated figure](assets/813d8fa6341056e6e7c9ee733cf9834c24a44df78a9d5a687f5d2a91b5cec940.png)

Red dots mark locations shared by at least 25 different projects. The map includes points already withheld from the project map. It shows recorded locations, not verified infrastructure sites; lines, polygons and missing or invalid points are omitted.

## The records rarely tell us when construction happened

The shortage of actual start and finish dates limits comparisons of neighbourhood conditions before and after a project. Even a reported finish date does not confirm when a service became operational.

![Generated figure](assets/1bac5ac585ce6a91e8dc52563651a2567c115e4046d373f0d05ab7deb229f2c1.png)

Bars show how many distinct projects have each type of date. Registration records when a project entered the system; planned dates describe intentions. Neither substitutes for actual construction or opening dates.

## An available census value can conceal missing information

In 2022, racial-composition values are available for 99.24% of areas, but only 89.49% have all the required population counts. The existing calculation can treat a missing count as zero, so an available result does not always mean the underlying information is complete.

![Generated figure](assets/c1d179b871b2719a0ebf047d210e00206c6c2c3623e30888b4378401b5bb5bf5.png)

Percentages are calculated across all 287,178 areas in each year. The chart separates available results from complete required information. It describes data coverage, not differences in infrastructure proximity.

Income here is an area average based on household heads; racial composition describes the residents. These measures cannot tell us the income of individual Black or Brown residents or establish why infrastructure is located where it is. Distances and regression results are not part of this assessment.
<!-- brazil:output gov_data_quality_summary end -->

[Supporting evidence, definitions and methods](gov_data_quality_annex.md)
