# Image Dataset Audit Tool

A lightweight Python tool for auditing image classification datasets before they are used in data analysis and computer vision workflows.

The project focuses on dataset structure, image integrity, class distribution, image formats, and image dimensions, producing machine-readable outputs and a human-readable audit report without modifying the original dataset.

## Project Status

**Status:** In development
**Current milestone:** M1 — Dataset Discovery
**Version:** 0.1.0

## Motivation

Image datasets can contain structural and quality issues that are easy to overlook before analysis or model development.

Examples include:

* unexpected class distributions;
* corrupted or unreadable images;
* inconsistent image formats;
* heterogeneous image dimensions;
* empty classes;
* severe differences in the number of images between classes;
* unsupported files mixed with dataset images.

The Image Dataset Audit Tool aims to provide a simple, reproducible, and read-only way to identify and summarize these characteristics before downstream analysis or computer vision experiments.

## Scope

Version 1.0 is designed for image classification datasets organized by directories.

Each first-level directory under the dataset root represents a class.

Example:

```text
dataset/
├── class_a/
│   ├── image_001.jpg
│   └── image_002.png
├── class_b/
│   ├── image_003.jpg
│   └── image_004.jpg
└── class_c/
    └── image_005.png
```

Files located below a class directory belong to that class.

The audit process is read-only. Source datasets are never modified, moved, renamed, resized, converted, or deleted.

## Version 1.0 Features

The first version will provide:

* dataset path validation;
* automatic class discovery;
* image discovery;
* total image count;
* image count per class;
* class distribution percentages;
* image extension and format detection;
* image width and height inspection;
* corrupted or unreadable image detection;
* empty-class detection;
* basic class imbalance analysis;
* basic image-dimension statistics;
* terminal execution summary;
* detailed CSV output;
* structured JSON summary;
* human-readable PDF audit report;
* local Python execution;
* reproducible execution through Docker;
* compatibility with environments such as Google Colab.

## Supported Dataset Structure

Version 1.0 assumes that the dataset root contains one directory per class.

First-level directories define class labels.

Nested files inside each class directory may be discovered recursively while retaining the first-level directory as their class.

Dataset layouts based on explicit `train`, `validation`, and `test` partitions are outside the initial scope and may be considered in a future project.

## Planned Image Extensions

The initial implementation will focus on common image extensions supported by the selected image-processing library, including:

* `.jpg`;
* `.jpeg`;
* `.png`;
* `.bmp`;
* `.tif`;
* `.tiff`;
* `.webp`.

File extensions and detected image formats will be stored separately whenever possible so that inconsistencies can be identified.

## Outputs

A completed audit will generate a report directory containing:

```text
reports/
├── images.csv
├── summary.json
└── audit_report.pdf
```

### `images.csv`

The detailed CSV report will contain one record for each inspected image candidate.

Planned fields include:

```text
path
class
extension
format
width
height
status
error
```

Paths stored in reports should be relative to the dataset root whenever possible.

### `summary.json`

The JSON report will contain aggregated dataset information such as:

* total image count;
* total valid images;
* corrupted image count;
* number of classes;
* image count per class;
* class percentages;
* empty classes;
* detected image formats;
* image-dimension statistics;
* class imbalance ratio;
* unsupported or skipped file counts.

### `audit_report.pdf`

The PDF report will provide a concise human-readable overview containing:

* dataset summary;
* class-distribution table;
* class-distribution visualization;
* image-format summary;
* image-dimension statistics;
* corrupted-file summary;
* class imbalance information;
* relevant data-quality warnings.

## Execution Environments

The core implementation will remain independent of a specific execution environment.

### Local Python

Local Python execution will be the primary development and usage workflow.

### Docker

Docker will provide a reproducible and portable runtime environment.

Docker is included to standardize dependencies and execution, not to provide additional computational resources.

Input datasets and generated reports will remain outside the container through mounted directories.

### Google Colab

The same Python implementation should also be usable from Google Colab.

A later demonstration notebook may provide workflows for:

* mounting Google Drive;
* reading datasets stored in Drive;
* running the audit;
* persisting generated reports back to Drive.

Colab-specific code will not duplicate the core audit implementation.

## Non-Goals

Version 1.0 will not include:

* machine-learning model training;
* model inference;
* image classification;
* object detection;
* automatic dataset correction;
* automatic class balancing;
* data augmentation;
* automatic file renaming;
* automatic dataset reorganization;
* train/validation/test split generation;
* database integration;
* REST APIs;
* graphical or web interfaces;
* distributed processing;
* GPU-specific processing;
* DICOM-specific analysis;
* duplicate-image detection;
* visual-similarity analysis;
* automatic Kaggle dataset acquisition;
* patient-level medical dataset validation.

Dataset acquisition, transformation, and preparation are intentionally separated from the audit responsibility and may become a different future project.

## Development Milestones

### M0 — Scope & Requirements

Define the problem, scope, requirements, outputs, constraints, and completion criteria.

### M1 — Dataset Discovery

* validate the dataset path;
* discover classes;
* discover candidate image files;
* calculate initial file and class counts.

### M2 — Image Inspection

* validate image integrity;
* detect image format;
* collect width and height;
* register corrupted or unreadable files.

### M3 — Dataset Analysis

* calculate class distribution;
* calculate class percentages;
* identify empty classes;
* calculate basic dimension statistics;
* calculate a descriptive class imbalance indicator.

### M4 — Reporting

* terminal summary;
* CSV report;
* JSON summary;
* PDF report;
* basic visualizations.

### M5 — Packaging & Quality

* automated tests;
* error handling;
* Docker support;
* usage documentation;
* Google Colab demonstration;
* final project review.

## Requirements

The complete functional and non-functional requirements are maintained in:

[`docs/requirements.md`](docs/requirements.md)

## Development Principles

The project follows a small set of implementation principles:

* keep the scope proportional to the problem;
* prefer simple solutions over unnecessary architecture;
* keep dataset operations read-only;
* introduce dependencies only when they solve a concrete need;
* keep the core logic independent from execution environments;
* develop incrementally with automated tests;
* use small and meaningful Git commits;
* maintain reproducible execution.

## Planned Technology

The project will primarily use:

* Python;
* Pillow;
* Matplotlib;
* ReportLab;
* pytest;
* Docker.

Dependencies will be introduced incrementally when the corresponding functionality is implemented.

## Definition of Done

Version 1.0 will be considered complete when the application can:

* inspect a directory-based image classification dataset;
* identify classes and image files;
* count images globally and by class;
* identify image formats and dimensions;
* detect corrupted images without interrupting the complete audit;
* calculate class distribution and descriptive imbalance statistics;
* generate CSV, JSON, and PDF reports;
* provide a terminal summary;
* run locally;
* run through the documented Docker workflow;
* pass the main automated tests;
* provide clear installation and usage documentation.

## License

This project is licensed under the MIT License.
