from pathlib import Path
import pandas as pd
import backend.schemas.excel_schema as excel_schema
from backend.schemas.excel_schema import SubjectHours


def parse_excel_file(file_path: Path) -> excel_schema.ParsedExcel:
    df = pd.read_excel(file_path)
    df.drop(df.columns[-1], axis=1, inplace=True)
    df = concatenate_firsts_row(df)
    return get_values(df)


def concatenate_firsts_row(df: pd.DataFrame):
    row0 = df.iloc[0]
    row1 = df.iloc[1]

    new_data = {}
    for col in df.columns:
        val0 = row0[col]
        val1 = row1[col]

        first, second = None, None
        if pd.notna(val0):
            first = str(val0)
        if pd.notna(val1):
            second = str(val1)
        if (first and second) or second:
            new_data[col] = second
        elif first:
            new_data[col] = first
        else:
            new_data[col] = None

    new_row = pd.Series(new_data)

    df_new = df.iloc[2:].copy()
    df_new = pd.concat([pd.DataFrame([new_row]), df_new], ignore_index=True)
    return df_new


def get_values(df: pd.DataFrame):
    format_names = df.iloc[0].tolist()
    data = df.iloc[1:].reset_index(drop=True)
    lessons = []
    subjects = []
    sum_hours = 0

    for idx, row in data.iterrows():
        number = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
        name = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ''

        if 'I' in number or 'V' in number or 'X' in number:
            subjects.append(
                SubjectHours(
                    subject_name=name,
                    hours=0,
                )
            )
            continue

        thema_name = (number + ' ' + name).strip()

        if name == 'ВСЕГО':
            subjects[-1].hours = row.iloc[2]
            continue

        if thema_name == 'ИТОГО:':
            sum_hours = row.iloc[2]
            continue

        for col_idx in range(3, len(format_names)):
            if col_idx == 4:
                continue
            value = row.iloc[col_idx]
            if pd.notna(value):
                if isinstance(value, str):
                    try:
                        value = int(value.replace('*', ''))
                    except Exception as e:
                        pass
                if isinstance(value, int):
                    format_name = format_names[col_idx]
                    if not subjects:
                        subjects.append(
                            SubjectHours(
                                subject_name='Начальный предмет',
                                hours=value
                            )
                        )
                    lessons.append(excel_schema.ParsedPlan(
                        thema_name=thema_name,
                        hours=value,
                        format_name=format_name,
                        subject_name=subjects[-1].subject_name,
                    ))

    format_names.pop(4)
    format_names = format_names[3:]
    return excel_schema.ParsedExcel(
        subjects=subjects,
        format_names=format_names,
        lessons=lessons,
        sum_hours=sum_hours,
    )

    #TODO add parse "ВСЕГО"