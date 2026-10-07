---
name: "Public Gallery Asset Publisher"
description: "Uploads and publishes confirmed website-ready image assets after legal, privacy, metadata, and accessibility checks pass."
version: "1.0.0"
---

# Public Gallery Asset Publisher

Use this skill only after candidate images have passed public-release review.

## Preconditions

- Image quality filtering has removed unusable or blurry files.
- Copyright status and model releases have been checked.
- Faces, PII, and location-sensitive metadata have been reviewed.
- Approved images are converted and resized for the website.
- Accessibility captions and SEO metadata are prepared.

## Bound actions

1. Detect faces and PII before publication.
2. Check model-release status.
3. Remove EXIF metadata from approved assets.
4. Upload approved final assets to the CMS.
5. Publish only reviewed assets.

## Scope

- This skill does not publish raw photos.
- This skill does not decide legal clearance from filenames alone.
- This skill does not skip privacy review, EXIF removal, or accessibility metadata.
