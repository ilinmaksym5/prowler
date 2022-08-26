import os
from os import path, remove

from colorama import Fore

from config.config import (
    csv_file_suffix,
    json_asff_file_suffix,
    json_file_suffix,
    output_file_timestamp,
    prowler_version,
    timestamp_iso,
    timestamp_utc,
)
from lib.check.models import Check_Report, load_check_metadata
from lib.outputs.models import (
    Check_Output_JSON,
    Check_Output_JSON_ASFF,
    Compliance,
    ProductFields,
    Resource,
    Severity,
)
from lib.outputs.outputs import (
    fill_file_descriptors,
    fill_json,
    fill_json_asff,
    generate_csv_fields,
    set_report_color,
)
from lib.utils.utils import hash_sha512, open_file
from providers.aws.models import AWS_Audit_Info


class Test_Outputs:
    def test_fill_file_descriptors(self):
        audited_account = "123456789012"
        output_directory = f"{os.path.dirname(os.path.realpath(__file__))}"
        csv_fields = generate_csv_fields()
        test_output_modes = [
            ["csv"],
            ["json"],
            ["json-asff"],
            ["csv", "json"],
            ["csv", "json", "json-asff"],
        ]
        output_filename = f"prowler-output-{audited_account}-{output_file_timestamp}"
        expected = [
            {
                "csv": open_file(
                    f"{output_directory}/{output_filename}{csv_file_suffix}",
                    "a",
                )
            },
            {
                "json": open_file(
                    f"{output_directory}/{output_filename}{json_file_suffix}",
                    "a",
                )
            },
            {
                "json-asff": open_file(
                    f"{output_directory}/{output_filename}{json_asff_file_suffix}",
                    "a",
                )
            },
            {
                "csv": open_file(
                    f"{output_directory}/{output_filename}{csv_file_suffix}",
                    "a",
                ),
                "json": open_file(
                    f"{output_directory}/{output_filename}{json_file_suffix}",
                    "a",
                ),
            },
            {
                "csv": open_file(
                    f"{output_directory}/{output_filename}{csv_file_suffix}",
                    "a",
                ),
                "json": open_file(
                    f"{output_directory}/{output_filename}{json_file_suffix}",
                    "a",
                ),
                "json-asff": open_file(
                    f"{output_directory}/{output_filename}{json_asff_file_suffix}",
                    "a",
                ),
            },
        ]

        for index, output_mode_list in enumerate(test_output_modes):
            test_output_file_descriptors = fill_file_descriptors(
                output_mode_list,
                output_directory,
                csv_fields,
                output_filename,
            )
            for output_mode in output_mode_list:
                assert (
                    test_output_file_descriptors[output_mode].name
                    == expected[index][output_mode].name
                )
                remove(expected[index][output_mode].name)

    def test_set_report_color(self):
        test_status = ["PASS", "FAIL", "ERROR", "WARNING"]
        test_colors = [Fore.GREEN, Fore.RED, Fore.BLACK, Fore.YELLOW]

        for status in test_status:
            assert set_report_color(status) in test_colors

    def test_generate_csv_fields(self):
        expected = [
            "assessment_start_time",
            "finding_unique_id",
            "provider",
            "profile",
            "account_id",
            "account_name",
            "account_email",
            "account_arn",
            "account_org",
            "account_tags",
            "region",
            "check_id",
            "check_title",
            "check_type",
            "status",
            "status_extended",
            "service_name",
            "subservice_name",
            "severity",
            "resource_id",
            "resource_arn",
            "resource_type",
            "resource_details",
            "resource_tags",
            "description",
            "risk",
            "related_url",
            "remediation_recommendation_text",
            "remediation_recommendation_url",
            "remediation_recommendation_code_nativeiac",
            "remediation_recommendation_code_terraform",
            "remediation_recommendation_code_cli",
            "remediation_recommendation_code_other",
            "categories",
            "depends_on",
            "related_to",
            "notes",
            "compliance",
        ]

        assert generate_csv_fields() == expected

    def test_fill_json(self):
        input_audit_info = AWS_Audit_Info(
            original_session=None,
            audit_session=None,
            audited_account="123456789012",
            audited_identity_arn="test-arn",
            audited_user_id="test",
            audited_partition="aws",
            profile="default",
            profile_region="eu-west-1",
            credentials=None,
            assumed_role_info=None,
            audited_regions=["eu-west-2", "eu-west-1"],
            organizations_metadata=None,
        )
        finding = Check_Report(
            load_check_metadata(
                f"{path.dirname(path.realpath(__file__))}/fixtures/metadata.json"
            )
        )
        finding.resource_details = "Test resource details"
        finding.resource_id = "test-resource"
        finding.resource_arn = "test-arn"
        finding.region = "eu-west-1"
        finding.status = "PASS"
        finding.status_extended = "This is a test"

        input = Check_Output_JSON(**finding.check_metadata.dict())

        expected = Check_Output_JSON(**finding.check_metadata.dict())
        expected.AssessmentStartTime = timestamp_iso
        expected.FindingUniqueId = ""
        expected.Profile = "default"
        expected.AccountId = "123456789012"
        expected.OrganizationsInfo = None
        expected.Region = "eu-west-1"
        expected.Status = "PASS"
        expected.StatusExtended = "This is a test"
        expected.ResourceId = "test-resource"
        expected.ResourceArn = "test-arn"
        expected.ResourceDetails = "Test resource details"

        assert fill_json(input, input_audit_info, finding) == expected

    def test_fill_json_asff(self):
        input_audit_info = AWS_Audit_Info(
            original_session=None,
            audit_session=None,
            audited_account="123456789012",
            audited_identity_arn="test-arn",
            audited_user_id="test",
            audited_partition="aws",
            profile="default",
            profile_region="eu-west-1",
            credentials=None,
            assumed_role_info=None,
            audited_regions=["eu-west-2", "eu-west-1"],
            organizations_metadata=None,
        )
        finding = Check_Report(
            load_check_metadata(
                f"{path.dirname(path.realpath(__file__))}/fixtures/metadata.json"
            )
        )
        finding.resource_details = "Test resource details"
        finding.resource_id = "test-resource"
        finding.resource_arn = "test-arn"
        finding.region = "eu-west-1"
        finding.status = "PASS"
        finding.status_extended = "This is a test"

        input = Check_Output_JSON_ASFF()

        expected = Check_Output_JSON_ASFF()
        expected.Id = f"prowler-{finding.check_metadata.CheckID}-123456789012-eu-west-1-{hash_sha512('test-resource')}"
        expected.ProductArn = f"arn:aws:securityhub:eu-west-1::product/prowler/prowler"
        expected.ProductFields = ProductFields(
            ProviderVersion=prowler_version, ProwlerResourceName="test-resource"
        )
        expected.GeneratorId = "prowler-" + finding.check_metadata.CheckID
        expected.AwsAccountId = "123456789012"
        expected.Types = [finding.check_metadata.CheckType]
        expected.FirstObservedAt = (
            expected.UpdatedAt
        ) = expected.CreatedAt = timestamp_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        expected.Severity = Severity(Label=finding.check_metadata.Severity.upper())
        expected.Title = finding.check_metadata.CheckTitle
        expected.Description = finding.check_metadata.Description
        expected.Resources = [
            Resource(
                Id="test-resource",
                Type=finding.check_metadata.ResourceType,
                Partition="aws",
                Region="eu-west-1",
            )
        ]

        expected.Compliance = Compliance(
            Status="PASS" + "ED",
            RelatedRequirements=[finding.check_metadata.CheckType],
        )
        expected.Remediation = {
            "Recommendation": finding.check_metadata.Remediation.Recommendation
        }

        assert fill_json_asff(input, input_audit_info, finding) == expected