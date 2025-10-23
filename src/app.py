import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, Dash
from dash.exceptions import PreventUpdate
from dash import dash_table
import base64
import io
import dash_bootstrap_components as dbc
from numpy import interp

# Initialize the Dash app
app = Dash(prevent_initial_callbacks='initial_duplicate',external_stylesheets=[dbc.themes.COSMO])
server = app.server

row1 = html.Div(
    [
        dbc.Row([
            dbc.Col([
                html.H1("Science department grade calculator "),
                html.A("Tutorial for downloading the necessary files from Canvas", href="https://www.youtube.com/watch?v=B8JD7nMiWZk", target="_blank"),
                html.H5("First, upload your formative file and confirm that its contents look right. You should see a table with students, some student info, and all of your formative assignments and grades if you scroll to the right. "),
                html.H5("Second, upload your summative file and confirm that its contents look right. It will appear below the first table, so you may have to scroll down. You should see a table with students, some student info, and all of your Learning Targets, with numbers between 0 and 4 for all of the values."),
                html.H5("If your files look wrong, you can always refresh the page to try again"),
                html.H5("If all the data looks good, click the 'Run the grades' button at the very bottom"),
            ],
                style = {'margin-left':'5px', 'margin-top':'7px', 'margin-right':'5px'}
            )
        ])
    ]
)

row2 = html.Div(
    [
        dbc.Row([
            dbc.Col([
                dcc.Upload(
                    id='formative-data',
                    children=html.Div(['Formative: Drag and Drop or ', html.A('Select')]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=False),
            ]),
            dbc.Col([
                dcc.Upload(
                    id='summative-data',
                        children=html.Div(['Summative ("Outcomes"): Drag and Drop or ', html.A('Select ')]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=False),
            ])
        ]),

        dbc.Row([
            dcc.Checklist(
                id = "my_checklist",
                options=['Check for Biology Class'],
                value=[]
            )]),
        dbc.Row([
            dcc.Checklist(
                id = "my_checklist2",
                options=['Check for _Physics Class'],
                value=[]
            )]),
        dbc.Row([
            dbc.Col([
                html.H5("The default class selection is Adv. Physics. Choose an alternative if applicable:"),
            ],
                style = {'margin-left':'5px', 'margin-top':'7px', 'margin-right':'5px'}
            )
        ])
    ]
)

row3 = html.Div([
    dbc.Row([
        dbc.Col([html.Div(id='output-data-upload1')]),
        dbc.Col([html.Div(id='output-data-upload2')]),
    ]),
    dbc.Row([
        dbc.Col([html.Button('Run the grades calculation', id='merge-data-btn', n_clicks=0, style={'margin': '10px'})])
    ])
])

row4 = html.Div([
    dbc.Row([
        dbc.Col([html.Div(id='output-data-upload3')])
    ]),
        # dbc.Row([
        # dbc.Col([html.Div([
        #     html.Button("Download CSV", id="btn_csv"),
        #     dcc.Download(id="download-dataframe-csv"),
        # ])])
   # ])
])

app.layout = dbc.Container(children=[
    row1,
    html.Br(),
    row2,
    html.Br(),
    row3,
    html.Br(),
    row4
])

# Function to parse contents of uploaded CSV file
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    # Decode the base64 encoded string
    decoded = base64.b64decode(content_string)

    # Read the decoded bytes into a pandas DataFrame
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    return df

# Helper function for interpolations
def interpolate_and_return(grade, grade_range, pct_range, label):
    pctGrade = interp(grade, grade_range, pct_range)
    return [pctGrade, label]


# LT letter grade conversion for Honors
def percentGradeH(LT_grade):

    grade_categories = [
        (3.40, 4.00, [93, 100], "H A"),
        (3.20, 3.3999999, [90, 93], "H A-"),
        (3.05, 3.1999999, [87, 90], "H B+"),
        (2.80, 3.0499999, [83, 87], "H B"),
        (2.65, 2.7999999, [80, 83], "H B-"),
        (2.40, 2.6499999, [77, 80], "H C+"),
        (2.25, 2.3999999, [73, 77], "H C"),
        (2.00, 2.2499999, [70, 73], "C-"),
        (1.75, 1.9999999, [67, 70], "D+"),
        (1.50, 1.7499999, [63, 67], "D"),
        (1.30, 1.4999999, [60, 63], "D-"),
        (1.00, 1.2999999, [50, 59.999], "F"),
        (0.00, 0.9999999, [0, 50], "F")
    ]
    
    for lower_bound, upper_bound, pct_range, label in grade_categories:
        if lower_bound <= LT_grade < upper_bound:
            return interpolate_and_return(LT_grade, [lower_bound, upper_bound], pct_range, label)

    # Handle out-of-range values
    return [None, "Invalid grade"]

# LT letter grade conversion for standard
def percentGradeAdv(LT_grade):

    grade_categories = [
        (3.00, 4.00, [93, 100], "Adv A"),
        (2.85, 2.999999, [90, 93], "Adv A-"),
        (2.70, 2.8499999, [87, 90], "Adv B+"),
        (2.55, 2.699999, [83, 87], "Adv B"),
        (2.40, 2.5499999, [80, 83], "Adv B-"),
        (2.20, 2.399999, [77, 80], "Adv C+"),
        (2.00, 2.199999, [73, 77], "Adv C"),
        (1.85, 1.99999, [70, 73], "C-"),
        (1.65, 1.849999, [67, 70], "D+"),
        (1.50, 1.649999, [63, 67], "D"),
        (1.30, 1.49999, [60, 63], "D-"),
        (1.00, 1.299999, [50, 59.999], "F"),
        (0.0, 0.99999, [0, 50], "F")
    ]

    for lower_bound, upper_bound, pct_range, label in grade_categories:
        if lower_bound <= LT_grade < upper_bound:
            return interpolate_and_return(LT_grade, [lower_bound, upper_bound], pct_range, label)

    # Handle out-of-range values
    return [None, "Invalid grade"]

# Callback to upload formative file
@app.callback(Output('output-data-upload1', 'children'),
              [Input('formative-data', 'contents'),
               Input('formative-data', 'filename')])
def upload_file_1(contents, filename):
    if contents is None:
        raise PreventUpdate

    df1 = parse_contents(contents, filename)
    return html.Div([
        html.H2(f'Successfully uploaded {filename}.'),
        html.H4('Please confirm that this data looks right before uploading the Summative file'),
        dash_table.DataTable(
            columns=[{'name': col, 'id': col} for col in df1.columns],
            data=df1.to_dict('records'),
            fill_width=False
        )
    ])

# Callback to upload summative file
@app.callback(Output('output-data-upload2', 'children'),
              [Input('summative-data', 'contents'),
               Input('summative-data', 'filename')])
def upload_file_2(contents, filename):
    if contents is None:
        raise PreventUpdate

    df2 = parse_contents(contents, filename)
    return html.Div([
        html.H2(f'Successfully uploaded: {filename}.'),
        html.H4('Please confirm that this data looks right before clicking the "Run grades" button below'),
        dash_table.DataTable(
            columns=[{'name': col, 'id': col} for col in df2.columns],
            data=df2.to_dict('records'),
            fill_width=False
        )
    ])

# Callback to clean and display data
@app.callback(
        Output('output-data-upload1', 'children', allow_duplicate=True),
        Output('output-data-upload2', 'children', allow_duplicate=True),
        Output('output-data-upload3', 'children'),
              [Input('merge-data-btn', 'n_clicks'),
               Input('my_checklist', component_property='value')],
              [dash.dependencies.State('formative-data', 'contents'),
               dash.dependencies.State('formative-data', 'filename'),
               dash.dependencies.State('summative-data', 'contents'),
               dash.dependencies.State('summative-data', 'filename')])
def merge_and_display(n_clicks, biology, formative_contents, formative_filename, summative_contents, summative_filename):
    if n_clicks == 0:
        raise PreventUpdate


    if formative_contents is None or summative_contents is None:
        raise PreventUpdate

    # import formative data, keep only the one relevant column, name, and ID 
    f_df = parse_contents(formative_contents, formative_filename)

    if biology:
        f_df['Formative Pct Grade'] = list(f_df['Formative Assessments Current Score'])
    else:
        f_df['Formative Pct Grade'] = list(f_df['Formative Current Score']) 

    f_df = f_df[["Student", "ID", 'Section', 'Formative Pct Grade']]


    s_df = parse_contents(summative_contents, summative_filename)
    #s_df['LT Average'] = s_df.mean(numeric_only=True, axis=1)
    droppedColumnsLT = [i for i in s_df if "mastery points" in i]
    # droppedColumnsLT.append("Student ID") #keep this column for merging later
    droppedColumnsLT.append("Student SIS ID")
    s_df = s_df.drop(droppedColumnsLT, axis=1)
    s_df = s_df.dropna(how='all', axis=1,)
    s_df["LT Average"] = s_df.loc[:,[c for c in s_df.columns if c!= "Student ID"]].mean(axis=1)
    s_df = s_df[['Student name', 'Student ID', 'LT Average']]

    gradePercentageH = []
    gradeLetterH = []

    gradePercentageAdv = []
    gradeLetterAdv = []

    for num in s_df['LT Average']:

        pct = percentGradeH(num)[0]
        gradePercentageH.append(pct)

        pct = percentGradeAdv(num)[0]
        gradePercentageAdv.append(pct)

        lett = percentGradeH(num)[1]
        gradeLetterH.append(lett)

        lett = percentGradeAdv(num)[1]
        gradeLetterAdv.append(lett)

        #print(num, pct, lett)

    s_df['LT Letter Grade: H'] = gradeLetterH
    s_df['Summative Pct Grade: H'] = gradePercentageH

    s_df['LT Letter Grade: Adv'] = gradeLetterAdv
    s_df['Summative Pct Grade: Adv'] = gradePercentageAdv


    # renaming them to have a common column title
    f_df.rename(columns={"ID":"Student ID"}, inplace=True)

    # Merge dataframes based on a common column, using the ID was easier than trying to re-order the names to match (one was "first last", the other was "last, first")
    merged_df = pd.merge(f_df, s_df, on='Student ID', how='inner')
    merged_df = merged_df[['Student', 'Section', 'Formative Pct Grade','LT Average', 'LT Letter Grade: H', 'Summative Pct Grade: H', "LT Letter Grade: Adv",'Summative Pct Grade: Adv']]

    # I merged here with the Student ID so the "Points Possible" error never even matters on the web app. 
    # desktop version from merging by name is good too but this works fine so I'll leave it
    # MG January 2025

    formativeNumGrades = list(merged_df["Formative Pct Grade"])
    summativeNumGradesH = merged_df['Summative Pct Grade: H']
    summativeNumGradesAdv = merged_df['Summative Pct Grade: Adv']

    totalModGradeH=[]
    totalModGradeAdv=[]

    for i in range(len(list(summativeNumGradesH))):
        entry = .4*float(formativeNumGrades[i]) + .6*summativeNumGradesH[i]
        totalModGradeH.append(entry)

    for i in range(len(list(summativeNumGradesAdv))):
        entry = .4*float(formativeNumGrades[i]) + .6*summativeNumGradesAdv[i]
        totalModGradeAdv.append(entry)

    merged_df['Total Year Pct Grade: H'] = totalModGradeH
    merged_df['Total Year Pct Grade: Adv'] = totalModGradeAdv
    merged_df = merged_df.round(3)

    # Display the merged dataframe in a Dash DataTable
    return [
        html.Div(),
        html.Div(),
        html.Div([
            html.H2('Results for the year to date:'),
            html.H5("You can sort any of these columns by clicking the small arrows beside each column title. You can also search for a student, but it is case-sensitive. You can also delete any of the columns that aren't helpful to you, like the LT letter grades"),
            dash_table.DataTable(
                columns=[{'name': col, 'id': col, 'deletable': True} for col in merged_df.columns],
                data=merged_df.to_dict('records'),
                fill_width=False,
                sort_action='native',
                filter_action='native',
                export_format='csv'
            )
        ])
    ]

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)


# from dash_bootstrap_templates import load_figure_template
# load_figure_template('COSMO')

#to-do: import from the very base function in physicsGrading2425.py so there's less copy-pasting. Surely I can just add that to the main directory and reference it? 

# Hope to add: get an emailed copy every time the app is run

# Hope to add: could rename the exported file with the current date
# # Callback to export the final data
# @app.callback(
#     Output("download-dataframe-csv", "data"),
#     Input("btn_csv", "n_clicks"),
#     State("output-data-upload3", "children"),
#     prevent_initial_call=True,
# )
# def func(n_clicks, f_df):
#     return dcc.send_data_frame(f_df[2].to_csv, "mydf.csv")