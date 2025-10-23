from enum import Enum

from emodpy.utils.targeting_config import AbstractTargetingConfig, BaseTargetingConfig
from emodpy.utils.targeting_config import HasIP, HasIntervention, IsPregnant


class YesNoNa(Enum):
    """
    This enum is used in the Targeting_Config logic to indicate if a particular attribute
    should be yes, no, or na (not applicable/don't consider)
    """
    YES = "YES"
    NO  = "NO"    # noqa: E221
    NA  = "NA"    # noqa: E221


class MoreOrLess(Enum):
    """
    This enum is used in Targeting_Config logic to indicate if the check should be
    strictly less than, '<', or strictly greater than, '>'.  These are used when
    checking for the number of partners, months, etc.
    """
    LESS = "LESS" # less than '<'
    MORE = "MORE" # greater than '>'


class OfRelationshipType(Enum):
    """
    This enum is used in the Targeting_Config logic to indicate if the check should
    consider specific relationship types or not.  If the user selects a specific
    type, then the rest of the checks will only be for those types of relationships.
    If the user selects 'NA', then relationships of all types will be considered.
    """
    NA         = "NA"           # noqa: E221
    TRANSITORY = "TRANSITORY"
    INFORMAL   = "INFORMAL"     # noqa: E221
    MARITAL    = "MARITAL"      # noqa: E221
    COMMERCIAL = "COMMERCIAL"


class NumMonthsType(Enum):
    """
    This enum is used in the Targeting_Config logic to indicate the duration range
    to check how many partners a person has.  These ranges are fixed in EMOD and
    the user cannot indicate a random range.
    """
    THREE_MONTHS  = "THREE_MONTHS"   # noqa: E221
    SIX_MONTHS    = "SIX_MONTHS"     # noqa: E221
    NINE_MONTHS   = "NINE_MONTHS"    # noqa: E221
    TWELVE_MONTHS = "TWELVE_MONTHS"


class RecentlyType(Enum):
    """
    This enum is used in the Targeting_Config logic to indicate if we only want
    to consider people who have a relationship that just started or just ended.
    This means we are interested in relationships that started or stopped during
    the current time step.
    """
    NA      = "NA"       # noqa: E221
    STARTED = "STARTED"
    ENDED   = "ENDED"    # noqa: E221


class RelationshipTerminationReasonType(Enum):
    """
    This enum is used in the Targeting_Config logic to indicate if we are
    interested in a person because of WHY a relationship recently ended.
    For example, if a person BROKE_UP and has not other partners, we might
    want them to stop using PrEP.
    """

    NA = "NA"
    """
    The relationship has not been terminated.
    """

    BROKE_UP = "BROKEUP" # EMOD does not have the underscore
    """
    The relationship ended due to the duration settings.
    """

    SELF_MIGRATING = "SELF_MIGRATING"
    """
    One of the partners in the relationship has decided to migrate and
    so the relationship is terminated. Note: The user can control what
    happens to a relationship when there is migration; it does not have
    to terminate.
    """

    PARTNER_DIED = "PARTNER_DIED"
    """
    One of the partners died so the relationship was terminated.
    """

    PARTNER_TERMINATED = "PARTNER_TERMINATED"
    """
    This happens when the couple is separated due to migration and one
    of the partners decides to terminate the relationship.
    """

    PARTNER_MIGRATING = "PARTNER_MIGRATING"
    """
    The relationship is being terminated because one of the partners has
    another partner that is migrating. For example, a married couple is
    moving because the wife got a new job. The husband must terminate his
    other relationships with "PARTNER_MIGRATING".
    """


class IsCircumcised(BaseTargetingConfig):
    """
    Select the individual based on whether or not they are circumcised.
    """
    def __init__(self):
        super().__init__()
        self.class_name = "IsCircumcised"


class IsHivPositive(BaseTargetingConfig):
    """
    Select the individual based on whether or not they have HIV.  The "and_has_XXX"
    parameters extend this by being and'd with the check on whether or not the person
    has HIV.  For example, if you want to select people that are:

        * HIV negative
        * AND have been tested
        * AND have never tested positive

    you will create the following:

        >>> targeting_config = ~IsHivPositive( and_has_ever_been_tested=YesNoNa.YES,
        >>>                                    and_has_ever_tested_positive=YesNoNa.NO )

    Notice that if the person being considered was HIV positive, the rest of the checks
    would not matter because the first check was false.

    Also notice that when you invert IsHivPositive, you are only changing the whether
    or not you are looking for infected people.  It does not impact the "and_has_XXX" checks.

    Args:
        and_has_ever_been_tested: If the user sets this Enum to 'YES', then the
            individual's true infection status must equal to the inversion status and the
            person must have been tested at least once. Notice that this only tells if the
            has been tested, NOT that they tested positive. If set to 'NA' (default), then
            do not include this as part of the check.

        and_has_ever_tested_positive: If the user sets this Enum to 'YES', then the
            individual's true infection status must equal to the inversion status and the
            person must have tested POSITIVE at least once. Notice that this is different
            than just having been tested. However, it does not say the person received the
            results. If set to 'NA' (default), then do not include this as part of the check.

        and_has_received_positive_results: If the user sets this Enum to 'YES', then the
            individual's true infection status must equal to the inversion status and the
            last test result received was positive. If set to 'NA' (default), then do not
            include this as part of the check.
    """
    def __init__(self,
                 and_has_ever_been_tested:          YesNoNa = YesNoNa.NA,   # noqa: E241
                 and_has_ever_tested_positive:      YesNoNa = YesNoNa.NA,   # noqa: E241
                 and_has_received_positive_results: YesNoNa = YesNoNa.NA):
        super().__init__()
        self.class_name = "IsHivPositive"
        self.been_tested = and_has_ever_been_tested
        self.tested_positive = and_has_ever_tested_positive
        self.received_positive_results = and_has_received_positive_results

    def to_schema_dict(self, campaign):
        """
        Create the ReadOnlyDict object representation of this Targeting_Config logic.
        This is the dictionary used to generate the JSON for EMOD.

        Args:
            campaign: The campaign module that has the path to the schema

        Returns:
            A ReadOnlyDict object created by schema_to_class
        """
        tc_obj = super().to_schema_dict(campaign)
        tc_obj.And_Has_Ever_Been_Tested          = self.been_tested.value                # noqa: E221
        tc_obj.And_Has_Ever_Tested_Positive      = self.tested_positive.value            # noqa: E221
        tc_obj.And_Has_Received_Positive_Results = self.received_positive_results.value
        return tc_obj


class IsOnART(BaseTargetingConfig):
    """
    Select the individual based on whether or not they are actively on ART.
    """
    def __init__(self):
        super().__init__()
        self.class_name = "IsOnART"


class IsPostDebut(BaseTargetingConfig):
    """
    Select the individual based on whether or not they have reached sexual debut.
    """
    def __init__(self):
        super().__init__()
        self.class_name = "IsPostDebut"


class HasBeenOnArtMoreOrLessThanNumMonths(BaseTargetingConfig):
    """
    Determine if the individual has been on ART for less than "num" months.
    It will be false if the individual is not on ART. The test will be
    strictly less than.

    Args:
        num_months: This is the number of months that will be used in the test.
            The individual's duration on ART must be more or less than this value.
            NOTE: 1500 months is about 12 months / year * 125 years of max age

        more_or_less: This is used to determine if the check should be less than
            or greater than.
    """
    def __init__(self,
                 num_months: float = 1500.0,
                 more_or_less: MoreOrLess = MoreOrLess.LESS):
        super().__init__()
        self.class_name = "HasBeenOnArtMoreOrLessThanNumMonths"
        # TODO: use Ye's validate range check on num_months
        self.num_months = num_months
        self.more_or_less = more_or_less

    def to_schema_dict(self, campaign):
        """
        Create the ReadOnlyDict object representation of this Targeting_Config logic.
        This is the dictionary used to generate the JSON for EMOD.

        Args:
            campaign: The campaign module that has the path to the schema

        Returns:
            A ReadOnlyDict object created by schema_to_class
        """
        tc_obj = super().to_schema_dict(campaign)
        tc_obj.Num_Months   = self.num_months          # noqa: E221
        tc_obj.More_Or_Less = self.more_or_less.value
        return tc_obj


class HasMoreOrLessThanNumPartners(BaseTargetingConfig):
    """
    Determine if the individual has more or less than a specified number of active partners.
    This includes relationships that are paused due to migration. This test is strictly more
    or less than.

    Args:
        num_partners: This parameter allows the user to set the number of active
            partners/relationships that the individual must have more or less of.
            The value can range between 0 and 62.

        more_or_less: This is used to determine if the check should be less than
            or greater than.  The default value is 'LESS'.

        of_relationship_type: If the user sets this value to one of the four specific types
            (TRANSITORY, INFORMAL, MARITAL, COMMERCIAL), then the individual must have more or
            less relationships of this type. When the value is set to 'NA' (default), then it
            will count the relationships regardless of type.
    """
    def __init__(self,
                 num_partners: int = 0,
                 more_or_less: MoreOrLess = MoreOrLess.LESS,
                 of_relationship_type: OfRelationshipType = OfRelationshipType.NA):
        super().__init__()
        self.class_name = "HasMoreOrLessThanNumPartners"

        # TODO: use Ye's validate range method on num_partners
        self.num_partners = num_partners
        self.more_or_less = more_or_less
        self.of_relationship_type = of_relationship_type

    def to_schema_dict(self, campaign):
        """
        Create the ReadOnlyDict object representation of this Targeting_Config logic.
        This is the dictionary used to generate the JSON for EMOD.

        Args:
            campaign: The campaign module that has the path to the schema

        Returns:
            A ReadOnlyDict object created by schema_to_class
        """
        tc_obj = super().to_schema_dict(campaign)
        tc_obj.Num_Partners         = self.num_partners               # noqa: E221
        tc_obj.More_Or_Less         = self.more_or_less.value         # noqa: E221
        tc_obj.Of_Relationship_Type = self.of_relationship_type.value
        return tc_obj


class HasHadMultiplePartnersInLastNumMonths(BaseTargetingConfig):
    """
    Determine if the individual has had more than one relationship in the last "Num" months.
    This could constitute as "high-risk" behavior. The goal is to target people that have had
    coital acts with more than one person during the last X months. This would count current
    relationships, relationships that started in the last X months, and relationships that
    have ended in the last X months. Basically, all the relationships that have been active
    at some point during the last X months.

    NOTE: This only counts unique partners. Two relationships with the same person during
    the time period will count as one. For example, if you dated a person for three months,
    broke up, got back together after six months, and the time period was twelve months, then
    it would be considered one partner.

    NOTE: Also note that one partner can count across multiple periods.  For example, if the
    person has been in a MARITAL relationship for years, that partner will be counted in the
    last three months, last six months, last nine months, and last twelve months.  If the
    person started a relationship last month, it will only be counted within the last three
    months.

    Args:
        num_month_type: This parameter allows the user to set the maximum number of months
            from the current day to consider if the individual had multiple relationships.

        of_relationship_type: If the user sets this value to one of the four specific types
            (TRANSITORY, INFORMAL, MARITAL, COMMERCIAL), then the individual must have had
            more than one relationship of this type. When the value is set to 'NA' (default),
            then it just matters if the person had more than one relationship, regardless
            of type.
    """
    def __init__(self,
                 num_month_type: NumMonthsType = NumMonthsType.THREE_MONTHS,
                 of_relationship_type: OfRelationshipType = OfRelationshipType.NA):
        super().__init__()
        self.class_name = "HasHadMultiplePartnersInLastNumMonths"
        self.num_month_type = num_month_type
        self.of_relationship_type = of_relationship_type

    def to_schema_dict(self, campaign):
        """
        Create the ReadOnlyDict object representation of this Targeting_Config logic.
        This is the dictionary used to generate the JSON for EMOD.

        Args:
            campaign: The campaign module that has the path to the schema

        Returns:
            A ReadOnlyDict object created by schema_to_class
        """
        tc_obj = super().to_schema_dict(campaign)
        tc_obj.Num_Months_Type      = self.num_month_type.value       # noqa: E221
        tc_obj.Of_Relationship_Type = self.of_relationship_type.value
        return tc_obj


class HasCd4BetweenMinAndMax(BaseTargetingConfig):
    """
    Determine if the individual has a CD4 count that is between "min" and "max".
    The test is inclusive for "min" and exclusive for "max".

    Args:
        min_cd4: The minimum value of the test range. The individuals CD4 can be
            equal to this value to be considered "between".  The value can range
            from 0 to 1999 and must be less than 'max_cd4'.

        max_cd4: The maximum value of the test range. The individual's CD4 must be
            strictly less than this value to be considered "between".  The value
            can range from 0 to 2000 and must be greater than 'min_cd4'.
    """
    def __init__(self, min_cd4: float = 0, max_cd4: float = 2000):
        super().__init__()
        self.class_name = "HasCd4BetweenMinAndMax"

        # TODO: Use Ye's validate value range method
        if min_cd4 >= max_cd4:
            msg = f"Invalid 'min_cd4'={min_cd4} and 'max_cd4'={max_cd4}.\n"
            msg += "min_cd4' must be strictly less than 'max_cd4'."
            raise ValueError(msg)

        self.min_cd4 = min_cd4
        self.max_cd4 = max_cd4

    def to_schema_dict(self, campaign):
        """
        Create the ReadOnlyDict object representation of this Targeting_Config logic.
        This is the dictionary used to generate the JSON for EMOD.

        Args:
            campaign: The campaign module that has the path to the schema

        Returns:
            A ReadOnlyDict object created by schema_to_class
        """
        tc_obj = super().to_schema_dict(campaign)
        tc_obj.Min_CD4 = self.min_cd4
        tc_obj.Max_CD4 = self.max_cd4
        return tc_obj


class HasRelationship(BaseTargetingConfig):
    """
    This is used to select people who have a partner/relationship that meets certain
    qualifications.

    Args:
        of_relationship_type: If the user sets this value to one of the four specific
            types (TRANSITORY, INFORMAL, MARITAL, COMMERCIAL), then the individual must
            have at least one relationships of this type.(default).  The other constraints
            will be on these relationships.  If NA is selected, then all of the individual's
            relationships will be considered.

        that_recently: This parameter is used if the relationship being considered must have
            recently been started or ended. Possible values are:

            - NA (Default) - Do no consider That_Recently in the selection process.
            - STARTED - Only consider relationships that have started within one time-step.
                One should note that the relationships you see will depend on whether you are
                using NodeLevelHealthTriggeredIV (NLHTIV) [add_intervention_triggered()] or an
                event coordinator [add_intervention_scheduled()]. NLHTIV and the individuals
                will be updated after new relationships have been created so with this feature,
                NLHTIV will see relationships in the previous time step as well as the current
                time step.  An event coordinator executes BEFORE new relationships are formed
                so it will only see the relationships created in the previous time step.
            - ENDED - Check the status of the relationship that just ended. Note: This can only
                be used with NodeLevelHealthTriggeredIV listening for the 'ExitedRelationship'
                event.

        that_recently_ended_due_to: If That_Recently is set to 'ENDED', this is used to look at the
            reason the relationship ended. Possible values are:

            - NA (Default) - The relationship has not been terminated.
            - BROKE_UP - The relationship ended due to the duration settings.
            - SELF_MIGRATING - One of the partners in the relationship has decided to migrate and so
                the relationship is terminated. Note: the user can control what happens to a
                relationship when there is migration; it does not have to terminate.
            - PARTNER_MIGRATING - The relationship is being terminated because one of the partners
                has another partner that is migrating. For example, a married couple is moving because
                the wife got a new job. The husband must terminate his other relationships with 'PARTNER_MIGRATING'.
            - PARTNER_DIED - One of the partners died so the relationship was terminated.
            - PARTNER_TERMINATED - This happens when the couple is separated due to migration and one
                of the partners decides to terminate the relationship.

        with_partner_who: Given that the parameters about the relationship are true, this parameter
            is used to look at the partner of the relationship. It is a Targeting_Config so one uses
            the same classes to query the partner. For example, to find out if person has a partner
            with HIV, you could use IsHivPositive.
    """
    def __init__(self,
                 of_relationship_type:       OfRelationshipType                = OfRelationshipType.NA,                 # noqa: E221, E241
                 that_recently:              RecentlyType                      = RecentlyType.NA,                       # noqa: E221, E241
                 that_recently_ended_due_to: RelationshipTerminationReasonType = RelationshipTerminationReasonType.NA,
                 with_partner_who:           AbstractTargetingConfig           = None):                                 # noqa: E221, E241
        super().__init__()
        self.class_name = "HasRelationship"

        if (of_relationship_type == OfRelationshipType.NA) and\
           (that_recently        == RecentlyType.NA      ) and\
           (with_partner_who     is None                 ):      # noqa: E202, E272, E221
            msg = "No parameters were configured so no relationships would be targeted.\n"
            msg += "'HasRelationship' requires that you define at least one parameter."
            raise ValueError(msg)

        self.of_relationship_type       = of_relationship_type       # noqa: E221
        self.that_recently              = that_recently              # noqa: E221
        self.that_recently_ended_due_to = that_recently_ended_due_to
        self.with_partner_who           = with_partner_who           # noqa: E221

    def to_schema_dict(self, campaign):
        """
        Create the ReadOnlyDict object representation of this Targeting_Config logic.
        This is the dictionary used to generate the JSON for EMOD.

        Args:
            campaign: The campaign module that has the path to the schema

        Returns:
            A ReadOnlyDict object created by schema_to_class
        """
        tc_obj = super().to_schema_dict(campaign)
        tc_obj.Of_Relationship_Type       = self.of_relationship_type.value        # noqa: E221
        tc_obj.That_Recently              = self.that_recently.value               # noqa: E221
        tc_obj.That_Recently_Ended_Due_To = self.that_recently_ended_due_to.value

        if self.with_partner_who:
            tc_obj.With_Partner_Who = self.with_partner_who.to_schema_dict(campaign)

        return tc_obj

    def to_simple_dict(self, campaign):
        """
        Return a plain/simple dictionary of the expected JSON for EMOD.  The main
        purpose of this is for validation in testing.  We need the ability to see
        that the logic written in python is translated to the JSON correctly.

        Args:
            campaign: The campaign module that has the path to the schema

        Returns:
            A simple dictionary containing the data for EMOD.
        """
        tc_dict = super().to_simple_dict(campaign)
        if self.with_partner_who:
            # we need to convert this object here because it is easier to ensure the object
            # is converted to the simple dictionary.
            tc_dict["With_Partner_Who"] = self.with_partner_who.to_simple_dict(campaign)
        else:
            # This gets rid of the default stuff put into the dictionary
            del tc_dict["With_Partner_Who"]
        return tc_dict


# __all_exports: A list of classes that are intended to be exported from this module.

__all_exports = [
    AbstractTargetingConfig,
    BaseTargetingConfig,
    HasIP,
    HasIntervention,
    IsPregnant,
    YesNoNa,
    MoreOrLess,
    OfRelationshipType,
    NumMonthsType,
    RecentlyType,
    RelationshipTerminationReasonType,
    IsCircumcised,
    IsHivPositive,
    IsOnART,
    IsPostDebut,
    HasBeenOnArtMoreOrLessThanNumMonths,
    HasMoreOrLessThanNumPartners,
    HasHadMultiplePartnersInLastNumMonths,
    HasCd4BetweenMinAndMax,
    HasRelationship
]

# The following loop sets the __module__ attribute of each class in __all_exports to the name of the current module.
# This is done to ensure that when these classes are imported from this module, their __module__ attribute correctly
# reflects their source module.
# During the documentation build with Sphinx, these classes will be displayed as belonging to the 'emodpy_malaria' package,
# not the 'emodpy' package.
# For example, the 'PropertyRestrictions' class will be documented as 'emodpy_malaria.campaign.common.PropertyRestrictions(...)'.
# This is crucial for accurately representing the source of these classes in the documentation.

for _ in __all_exports:
    _.__module__ = __name__

# __all__: A list that defines the public interface of this module.
# This is essential to ensure that Sphinx builds documentation for these classes, including those that are imported
# from emodpy.
# It contains the names of all the classes that should be accessible when this module is imported using the syntax
# 'from module import *'.
# Here, it is set to the names of all classes in __all_exports.

__all__ = [_.__name__ for _ in __all_exports]
