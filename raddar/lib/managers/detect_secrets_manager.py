from detect_secrets.main import parse_args, _perform_scan
from detect_secrets.plugins.common import initialize
from detect_secrets.util import build_automaton
from sqlalchemy.orm import Session

from raddar.core import contexts
from raddar.crud import crud
from raddar.schemas import schemas
from raddar.core.settings import settings
from raddar.lib.managers.repository_manager import get_branch_name


def project_analysis(
    project_name: str, analysis: schemas.Analysis, scan_origin: str, db: Session
):
    branch_name = analysis.branch_name
    if branch_name:
        branch_name = get_branch_name(branch_name)

    with contexts.clone_repo(
        project_dir=settings.PROJECT_RESULTS_DIRNAME,
        project_name=project_name,
        ref_name=branch_name,
    ) as (repo, temp_dir):
        analysis_returned = crud.create_analysis(
            db=db,
            project=schemas.ProjectBase(name=project_name),
            branch_name=repo.active_branch.name,
            ref_name=repo.commit("HEAD").hexsha,
            scan_origin=scan_origin,
        )

        baseline = get_project_secrets(temp_dir, project_name)
        for file in baseline["results"]:
            for secret in baseline["results"][file]:
                new_secret = {}
                new_secret["filename"] = file.split(f"{temp_dir}/")[1]
                new_secret["secret_type"] = secret["type"]
                new_secret["line_number"] = secret["line_number"]
                new_secret["secret_hashed"] = secret["hashed_secret"]
                crud.create_analysis_secret(db, new_secret, analysis_returned.id)

        return analysis_returned


def get_project_secrets(project_results_dir: str, project_name: str) -> dict:
    argv = ["scan", f"{project_results_dir}/{project_name}"]

    args = parse_args(argv)

    automaton = None
    word_list_hash = None
    if args.word_list_file:
        automaton, word_list_hash = build_automaton(args.word_list_file)

    # Plugins are *always* rescanned with fresh settings, because
    # we want to get the latest updates.
    plugins = initialize.from_parser_builder(
        plugins_dict=args.plugins,
        custom_plugin_paths=args.custom_plugin_paths,
        exclude_lines_regex=args.exclude_lines,
        automaton=automaton,
        should_verify_secrets=not args.no_verify,
    )

    baseline_dict = _perform_scan(args, plugins, automaton, word_list_hash,)

    return baseline_dict
