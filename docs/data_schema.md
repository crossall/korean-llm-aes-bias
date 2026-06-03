# Flattened data schema

`scripts/01_flatten_aihub_json.py` converts nested AI Hub JSON label files into `data/processed/master_aihub_flat.csv`.
The main columns are:

| Column group | Examples | Meaning |
|---|---|---|
| Source trace | `outer_zip`, `outer_index`, `inner_zip`, `inner_index`, `inner_path`, `record_uid` | Exact archive origin. Duplicate nested archive names are preserved by index. |
| Item metadata | `question_id`, `grade`, `grade_num`, `subject`, `subject_code`, `topic`, `level`, `question_type`, `format`, `prompt`, `keyword` | Prompt and task metadata. |
| Student response metadata | `answer_id`, `region`, `gender`, `reference`, `text`, `answer_len_syllable`, `answer_len_word` | Student answer and basic metadata. |
| Human scores | `human_holistic_rater1`, `human_holistic_rater2`, `human_holistic_mean`, `human_task_1_mean`, ... | Two rater scores and means for holistic/analytic traits. |
| Rubric text | `rubric_task_1_name`, `rubric_task_1_evaluation_5`, ... | Analytic rubric text used to build LLM scoring prompts. |

Trait names:

```text
holistic
task_1
content_1, content_2, content_3
organization_1, organization_2
expression_1, expression_2
```

Notes:

- Holistic scores use a 1–4 scale.
- Analytic trait scores use a 1–5 scale.
- `format` is normalized as `descriptive` for 서술형 and `essay` for 논술형.
- `grade_num` maps 초5→5, 초6→6, 중1→7, 중3→9.
