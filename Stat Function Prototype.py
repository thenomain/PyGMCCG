"""
## STAT FUNCTION PROTOTYPE (SFP) ##
Behold the code, most of it guessed or pseudocode
or related by Pax or Chime.

A character sheet is a series of traits.
    ("Trait" is the term White Wolf and Onyx path use for sheet items.)
    (Yes, this is still the "Stat Function Prototype". Name's got history.)

If the value can affect other traits, it should be here, else not.
    (e.g., 'Concept' doesn't need to be here.)

Trait -> Type of Trait   -> Trait Group
         StringTrait     -> Clan
         NumericTrait    -> Attribute
         NumericTrait    -> Skill
         PoolTrait       -> Health
         MultivalueTrait -> Gift

STRING:
    Just some text.
NUMERIC:
    Permanent value and a possible series of offsets.
    Integers only.
POOL:
    Permanent (max) value and current value.
MULTI-VALUE:
    Dictionary of string traits indexed by string or numeric.


All traits may chain to another trait, e.g.:
    Medicine.First_Aid = 1
    print Medicine.First_Aid

Both 'Medicine' and 'First_Aid' are numeric, but the second relies on the first, or is a "substat" of the first.
In the first instance,'First_Aid' is set to 1, but only when referenced with 'Medicine':
    First_Aid == None
    Medicine.First_Aid == 1
In the second instance, because they are numeric, 'First_Aid' and 'Medicine' are returned as a total:
    Medicine + First_Aid


== DATA DICTIONARIES =====================================================================

Data dictionaries are the valid traits and important information about them.
Mainly they are there to expose the prettified name and tags.

Data Dictionaries are formatted in the following way:
    {
        "<trait name>": {"<extra>": <data>, ...},
        ...
    }

Extras include:
    "tag": (<string list of tags>)
    "value": (<values valid for this trait>)
    "template": (<string list of templates validated for this item, maybe should be code>)
    "prerequisite": <code to run to check if someone can take this>
    "prereq-text": "<text to show someone describing the prerequisite code>"

None of these extras are required, but must be in a `dict` format. e.g.:
    { "Strength": None }

It's unlikely this will happen.

example:
    merit_dictionary = {
        "Investigative Prodigy": {
            "value": (1, 2, 3, 4, 5),
            "template": "all",
            "tags": ("mental"),
            "prereq-text": "Wits 3+ and Investigation 3+",
            "prerequisite": "<mystery code goes here>",
            "book": "CoD p.45",
            "note": "See CoD p.95 for uncovering Clues"
        },
        "Automatic Writing": {
            "value": 2,
            "template": "human",
            "tags": ("supernatural"),
            "book": "CoD p.56",
            "note": "Risk of being haunted."
        }
    }


-- Data Dictionary: TAGS -----------------------------------------------------------------

Anything can be a tag. Some systems may use these for more complex checking.
For instance, a mage may add +1 to any "resistance" Attribute.

Here is a short list of tags and what they do:
    Social, Mental, Physical:
        Classification for Attributes, Skills, and sometimes Merits
    Power, Finesse, Resistance:
        Classification for Attributes
    Supernatural:
        Classification for Merits


"""

# == TRAIT ========================================================
class Trait(object):
    """
    A trait (stat) for World/Chronicle of Darkness.
    Shares several key items:
    - Name: What to display
    - Value: Its value
    - Substat: Another Trait object that relies on this one
    """

    def __init__(self, name, value=None):
        # underlined variables are 'private' or at least internal
        self._name = name  # prettified/display version of the name
        self._value = value
        self._substat = None

    # I doubt we need these, but who knows.
    @property
    def value(self):
        return self._value

    @property
    def name(self):
        return self._name

    @property
    def substat(self):
        return self._substat


# == TRAIT: NUMERIC =========================================================
class NumericTrait(Trait):
    """
    A numeric trait in WoD/CoD has a few key traits
    - Must be integer
    - Typically from 1-5 or 1-10
    - May have any number of offsets: temp boosts and/or penalties
    """

    # -- Numeric validation functions ---------------------------------------
    def checkint(self, value):
        try:
            test_value = int(value)
            return test_value
        except ValueError:
            raise ValueError("NumericTrait requires integer parameters")

    def checkrange(self, value):
        if self.min <= value <= self.max:
            return value
        else:
            raise ValueError("Value must be between %d and %d" % (self.min, self.max))

    # -- Numeric.__init__: Set initial value --------------------------------
    def __init__(self, name, value=0):
        self.min = 0
        self.max = 5
        self._offset = None

        test_value = self.checkint(value)
        test_value = self.checkrange(test_value)

        # now invoke the 'init' of the parent class
        super(NumericTrait, self).__init__(name, test_value)  # in Python3 :: super().__init__(name, test_value)

    # -- Numeric.Value: __set__, __get__, __add__ ---------------------------
    # @property: A great way to create a getter. `print numeric.value`
    # @<property>.setter: A great way to create a setter. `numeric.value = 3`
    # So we create `@property def value(self)` and then `@value.setter`.

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        test_value = self.checkint(value)
        test_sum = self.checkrange(self._value + test_value)
        self._value = test_sum

    def __set__(self, instance, value):
        """The plan here is to check range, max/min, and maybe offsets?"""
        self.value = value

    def __get__(self, other):
        """Get offsets?"""
        return self.value

    def __add__(self, value=0):
        """Add a value to a Numeric. Check it against "max" first."""
        self.value = self.value + value

    def __radd__(self, value=0):
        self.__add__(value)

    # -- Numeric.Offset -----------------------------------------------------

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, offset):
        """
        Offset is a dictionary of: reason:value
        :type offset: dict
        """
        assert type(offset) is dict, \
            "Offset must be Dict type in format: {'<reason>': <value>, ...}"

        """
        for each item in offset:
            key must be string
            value must be int <> 0
        """
        for key, value in offset:
            if type(key) != str:
                raise ValueError("Key '%r' must be a string" % key)
            elif (type(value) != int) || (value == 0):
                raise ValueError("Value '%r' must be a non-zero integer" % value)
            elif key in self._offset:
                raise ValueError("Key '%s' already in offset" % key)

        # it's clear: merge the two dictionaries
        self._offset.update(offset)

    def offset_sum(self):
        """Output the numerical sum of all the offsets."""
        temp_sum = 0
        for key, value in self._offset:
            temp_sum += value
        return temp_sum

# == TRAIT: NUMERIC: ATTRIBUTE ==============================================
class Attribute(NumericTrait):
    """
    An Attribute is a numeric trait from 1-5.
    Its name can be one of the nine game Attributes with a combination of two categories:
        Strength (Physical, Force)
        Dexterity (Physical, Finesse)
        Stamina (Physical, Resistance)
        Charisma (Social, Force)
        Manipulation (Social, Finesse)
        Composure (Social, Resistance)
        Intelligence (Mental, Force)
        Wits (Mental, Finesse)
        Resolve (Mental, Resistance)

    Certain supernatural creatures can raise their Attribute max above 5.
    """

    attribute_dictionary = {
        'Strength':     {'tags': ('Physical', 'Force')},
        'Dexterity':    {'tags': ('Physical', 'Finesse')},
        'Stamina':      {'tags': ('Physical', 'Resistance')},
        'Charisma':     {'tags': ('Social', 'Force')},
        'Manipulation': {'tags': ('Social', 'Finesse')},
        'Composure':    {'tags': ('Social', 'Resistance')},
        'Intelligence': {'tags': ('Mental', 'Force')},
        'Wits':         {'tags': ('Mental', 'Finesse')},
        'Resolve':      {'tags': ('Mental', 'Resistance')}
    }

    def checkname(self, name):
        """
        Checkname takes a partial name match and returns the closest "pretty name".

        Code will error if too many matches, but we can easily change that to the first sorted match.
        """

        # I almost know how this works but I'm glad that it does.
        # Sorted list of keys that start with `<name>*`. Case insensitive.
        temp_list = [key for key in sorted(self.attribute_dictionary) if name.lower() in key.lower()]

        # the following maintains key/value pair:
        # new_list = [key for key, value in sorted(self.attribute_dictionary.items()) if name.lower() in key.lower()]

        if len(temp_list) == 0:
            raise ValueError("No match")
        elif len(temp_list ) > 1:
            raise ValueError("Too many matches: %r" % temp_list)
        else:
            return temp_list[0]

    def __init__(self, name, value=1):
        self.min = 1
        temp_name = self.checkname(name)

        # now invoke the 'init' of the parent class
        super(Attribute, self).__init__(temp_name, value)  # in Python3 :: super().__init__(name, value)
