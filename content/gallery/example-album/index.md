+++
title = "Example Album"
description = "Replace this with a real album of painted miniatures."
date = 2026-06-25
showDate = false
showAuthor = false
showReadingTime = false
showWordCount = false
# featureImage = "01.jpg" # uncomment and set to one of the images below for the section card thumbnail
+++

A short intro for this album.

{{< gallery >}}
  <img src="01.jpg" class="grid-w33" />
  <img src="02.jpg" class="grid-w33" />
  <img src="03.jpg" class="grid-w33" />
{{< /gallery >}}

<!--
HOW TO ADD A NEW ALBUM:
1. Duplicate this folder: content/gallery/<your-album-name>/
2. Drop your web-optimised images (≈1800px, 200–500KB) into that folder.
3. Reference each image by filename inside the {{</* gallery */>}} shortcode.
   Grid width classes: grid-w33 (3 per row), grid-w50 (2 per row), grid-w100 (full width).
Images are referenced as page-bundle resources, so just the filename is needed.
-->
