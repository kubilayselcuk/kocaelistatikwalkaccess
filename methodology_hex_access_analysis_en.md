# Hex-Based Pedestrian Access Analysis Module

## Purpose

This module evaluates pedestrian accessibility to daily urban destinations through a hexagonal spatial grid. Each hexagon is treated as an analysis unit and classified according to walking-time proximity, destination availability, and the diversity of accessible options within a 15-minute walking threshold.

The method is designed to reveal areas with strong, moderate, limited, or no pedestrian access across multiple public-service and daily-use themes.

## Analysis Unit

The analysis uses a hexagonal grid as the common spatial unit. For each hexagon, accessibility values are calculated in relation to the nearest relevant destination and to the number of reachable destinations within defined walking-time bands.

Using a hex grid allows different destination themes to be compared on the same spatial framework and reduces the visual bias that can occur with irregular administrative boundaries.

## Destination Themes

The module can be applied to the following destination groups:

- Health facilities
- Schools
- Public-service uses
- Commercial areas
- Sports facilities
- Social and community facilities
- Recreation areas
- Bus stops
- Rail-system stops

Each destination theme is evaluated separately, while the resulting layers remain comparable because they share the same hexagonal base.

## Core Metrics

Three complementary analyses are produced for each destination theme.

### Analysis 1: Nearest Destination Access

This analysis measures each hexagon's access condition based on the walking time to the nearest destination in the selected theme.

Classification:

- Less than 15 minutes: Accessible
- 15 to 20 minutes: Moderate access
- 20 to 25 minutes: Limited access
- 25 minutes or more: No pedestrian access

This layer provides the broadest reading of whether a hexagon can reach at least one relevant destination within a practical walking distance.

### Analysis 2: Multi-Option Access Within 15 Minutes

This analysis evaluates not only proximity, but also the number and relative quality of destination options reachable within 15 minutes.

The assessment considers:

- Number of reachable destinations within 15 minutes
- Distance to the nearest destination
- A weighted access score using `1/rank`, where higher-ranked access categories contribute more strongly to the final classification

Areas with several reachable options and shorter walking distances are interpreted as having stronger access. Areas with only limited or distant options receive weaker access classifications.

### Analysis 3: First-Contact Access Within 15 Minutes

This analysis focuses on the minimum walking time required to reach at least one destination in the selected theme. It is intended to show the quality of first-contact pedestrian access.

Classification:

- 0 to 5 minutes: Very good access
- 5 to 10 minutes: Moderate access
- 10 to 15 minutes: Limited access
- 15 minutes or more: No pedestrian access

This layer highlights the areas where the first reachable service or facility is close enough to support everyday pedestrian use.

## Access Classes

The module uses the following shared access classes:

- Very good access
- Accessible
- Moderate access
- Limited access
- No pedestrian access

For map interpretation, stronger access classes are represented with green tones, while decreasing access levels transition through yellow and orange toward red for areas without pedestrian access.

## Outputs

For each destination theme, the module produces:

- A hex-level accessibility layer for Analysis 1
- A hex-level accessibility layer for Analysis 2
- A hex-level accessibility layer for Analysis 3
- A distribution summary showing the number of hexagons in each access class
- A comparable map legend using consistent colors and class names

## Interpretation

The three analyses should be read together rather than as substitutes for one another.

Analysis 1 shows whether a destination is reachable within a general walking threshold. Analysis 2 reveals whether residents have multiple nearby options or depend on a single accessible destination. Analysis 3 provides a more sensitive reading of immediate access quality by distinguishing very short walking times from longer trips within the 15-minute threshold.

Together, these layers identify places where access is robust, where service options are thin, and where pedestrian access gaps may require planning intervention.
