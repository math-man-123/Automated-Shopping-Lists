# Introduction
This project provides a Rasberry Pi based system to scan recipe QR codes and automatically print out shopping lists sorted by the actual store layout. A [full write-up](https://philsfun.com/printer/index.html) can be read on my website.

<p align="center">
<img width="600" alt="example" src="https://github.com/user-attachments/assets/776238a6-bce2-414e-b6d5-6e3d719d5b8a" />
</p>

# Overview
To go from selected recipes to a printed shopping list, the following pipeline is followed. 
* Take an image of the QR codes (via the integrated camera), preprocess them, and then extract the recipe ID using OpenCV.
* Get all the recipe ingredients from ID.json, add them up accordingly, and then sort them into sections as described in sections_data.json (e.g. store layout).
* Print a formatted list using a small thermal printer via ESC/POS (basically it's a receipt printer commonly found in stores).

# Features
Creates sorted shopping lists from scanned QR codes. Can handle both unknown recipes (QR codes) and unknown ingredients. Adds up multiples of the same ingredient, respecting their units (i.e. "g" and "kg" are merged correctly). Fully realized and integrated on a Raspberry Pi (just turn it on and wait a moment).
