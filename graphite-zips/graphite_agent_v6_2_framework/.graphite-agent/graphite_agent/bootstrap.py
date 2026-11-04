from .artefact_writer import ArtefactWriter
from .branch_classifier import BranchClassifier
from .config import load_config
from .executor import StrictExecutor
from .git_adapter import GitAdapter
from .github_provider import GitHubPullRequestProvider
from .graphite_client import GraphiteClient
from .ids import IdFactory
from .invariant_verifier import InvariantVerifier
from .pipeline import AnalysisPipeline
from .plan_compiler import PlanCompiler
from .plan_reader import ExecutionPlanReader
from .policy import ConservativeGraphitePolicy
from .post_action_verifier import PostActionVerifier
from .relationship_collector import RelationshipCollector
from .triage import GuidedTriage


def build_analysis_pipeline():
    config = load_config()
    ids = IdFactory()
    git = GitAdapter(config.primary_remote)
    provider = GitHubPullRequestProvider(git)
    policy = ConservativeGraphitePolicy()
    verifier = InvariantVerifier(config, git)
    collector = RelationshipCollector(config, git, ids)
    classifier = BranchClassifier(config, verifier, policy)
    compiler = PlanCompiler(ids, policy, config.schema_version)
    writer = ArtefactWriter(config.output_dir, config.write_legacy_aliases)
    return AnalysisPipeline(
        config, provider, collector, classifier, compiler, writer, policy
    )


def build_executor(enable_post_action_verification=True):
    config = load_config()
    git = GitAdapter(config.primary_remote)
    graphite = GraphiteClient(git)
    reader = ExecutionPlanReader(f"{config.output_dir}/execution_plan.json")
    verifier = (
        PostActionVerifier(build_analysis_pipeline)
        if enable_post_action_verification
        else None
    )
    return StrictExecutor(reader, graphite, verifier)


def build_triage():
    return GuidedTriage(load_config().output_dir)
