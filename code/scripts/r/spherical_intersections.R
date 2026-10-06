# WHY: retain sf/S2 semantics while avoiding its quadratic all-pairs dispatch.
indexed_intersections <- function(old_selected, newer_selected) {
  # WHY: sf's spherical all-pairs implementation is quadratic; prefilter exact S2 candidates.
  candidates <- st_intersects(newer_selected, old_selected, model="closed")
  old_index <- unlist(candidates, use.names=FALSE)
  new_index <- rep(seq_along(candidates), lengths(candidates))
  pair_geometry <- st_intersection(st_geometry(old_selected)[old_index], st_geometry(newer_selected)[new_index], by_element=TRUE, model="semi-open")
  intersections <- st_sf(code_tract_2000=old_selected$code_tract_2000[old_index], code_tract_new=newer_selected$code_tract_new[new_index], geometry=pair_geometry)
  intersections <- intersections[!st_is_empty(intersections),]
  intersections
}
