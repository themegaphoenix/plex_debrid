from base import *
from ui.ui_print import *

class release:
    # Define release attributes
    def __init__(self, source, type, title, files, size, download, seeders=0):
        self.source = source
        self.type = type
        self.title = title
        self.files = files
        self.size = size
        self.download = download
        self.hash = ''
        if len(self.download) > 0:
            if regex.search(r'(?<=btih:).*?(?=&)', str(self.download[0]), regex.I):
                self.hash = regex.findall(r'(?<=btih:).*?(?=&)', str(self.download[0]), regex.I)[0]
        self.cached = []
        self.wanted = 0
        self.unwanted = 0
        self.seeders = seeders
        self.resolution = "0"
        if regex.search(r'(2160|1080|720|480)(?=p)', str(self.title), regex.I):
            self.resolution = regex.findall(r'(2160|1080|720|480)(?=p)', str(self.title), regex.I)[0]

    # Define when releases are Equal
    def __eq__(self, other):
        return self.title == other.title

class rename:
    replaceChars = [
        ['&', 'and'],
        ['ü', 'ue'],
        ['ä', 'ae'],
        ['ö', 'oe'],
        ['ß', 'ss'],
        ['é', 'e'],
        ['è', 'e'],
        ['sh!t', 'shit'],
        ['.', ''],
        [':', ''],
        ['(', ''],
        [')', ''],
        ['`', ''],
        ['´', ''],
        [',', ''],
        ['!', ''],
        ['?', ''],
        [' - ', ''],
        ["'", ''],
        ["\u200b", ''],
        [' ', '.']
    ]

    def __new__(self, string):
        string = string.lower()
        for specialChar, repl in self.replaceChars:
            string = string.replace(specialChar.lower(), repl.lower())
        string = regex.sub(r'\.+', ".", string)
        return string

class sort:
    def setup(cls, new=False):
        back = False
        while not back:
            ui_cls('Options/Settings/Scraper Settings/Versions')
            print("Currently defined versions: [" + '], ['.join(x[0] for x in sort.versions) + ']')
            print()
            print("0) Back")
            print("1) Edit versions")
            print("2) Add version")
            print()
            choice = input("Choose an action: ")
            if choice == '0':
                back = True
            elif choice == "1":
                back2 = False
                while not back2:
                    ui_cls('Options/Settings/Scraper Settings/Versions/Edit')
                    print("0) Back")
                    indices = []
                    for index, version in enumerate(sort.versions):
                        print(str(index + 1) + ') Edit version "' + version[0] + '"')
                        indices += [str(index + 1)]
                    print()
                    choice2 = input("Choose an action: ")
                    if choice2 in indices:
                        print()
                        default = sort.versions[int(choice2) - 1]
                        name = sort.versions[int(choice2) - 1][0]
                        sort.version.setup(name, default, new=False)
                    if choice2 == '0':
                        back2 = True
            elif choice == "2":
                ui_cls('Options/Settings/Scraper Settings/Versions/Add')
                names = []
                name = "Id rather be watching the 1999 cinematic masterpiece 'The Mummy'."
                names += [name]
                for version in sort.versions[:]:
                    names += [version[0]]
                while name in names:
                    name = input("Please provide a unique name for this version: ")
                print()
                default = copy.deepcopy(sort.versions[0])
                sort.version.setup(name, default, new=True)
                sort.versions += [default]
        return

    class version:
        def setup(name, version_, new=False):
            back = False
            default = version_[3]
            while not back:
                version_[0] = name
                if new:
                    ui_cls('Options/Settings/Scraper Settings/Versions/Add')
                    print(
                        'Your new version [' + name + '] has been filled with some default rules. You can add new ones or edit the existing rules.')
                else:
                    ui_cls('Options/Settings/Scraper Settings/Versions/Edit')
                print()
                print('Current settigns for version [' + name + ']:')
                print()
                print("name     : " + version_[0])
                print("media    : " + str(version_[1]) + " (not editable yet)")
                print("required : " + version_[2] + " (not editable yet)")
                print()
                print("0) Back")
                indices = []
                l_o = 0
                l_a = 0
                l_i = 0
                l_s = 0
                for index, rule in enumerate(default):
                    indices += [str(index + 1)]
                    if len(str(index + 1)) >= l_i:
                        l_i = len(str(index + 1)) + 1
                    if len(rule[0]) >= l_a:
                        l_a = len(rule[0]) + 1
                    if len(rule[1]) >= l_s:
                        l_s = len(rule[1]) + 1
                    if len(rule[2]) >= l_o:
                        l_o = len(rule[2]) + 1
                for index, rule in enumerate(default):
                    print(str(index + 1) + ')' + ' ' * (l_i - len(str(index + 1))) + rule[0] + ' ' * (
                                l_a - len(rule[0])) + ' ' + rule[1] + ' ' * (l_s - len(rule[1])) + ': ' + ' ' * (
                                        l_o - len(rule[2])) + rule[2] + '  ' + rule[3])
                print()
                print("Choose a rule to edit or add a new rule by typing 'add'")
                print("To rename this version, type 'rename'")
                if len(sort.versions) > 1:
                    print("To delete this version, type 'remove'")
                print()
                choice = input("Choose an action: ")
                print()
                if choice in indices:
                    sort.version.rule.setup(choice, default, new=False)
                elif choice == '0':
                    back = True
                elif choice == 'add':
                    sort.version.rule.setup(choice, default, new=True)
                elif choice == 'rename':
                    ui_cls('Options/Settings/Scraper Settings/Versions/Add')
                    names = []
                    for version in sort.versions[:]:
                        names += [version[0]]
                    for version in sort.versions[:]:
                        if version[0] == name:
                            break
                    while name in names:
                        name = input("Please provide a unique name for this version: ")
                    version[0] = name
                    print()
                elif choice == 'remove':
                    if len(sort.versions) > 1:
                        for version in sort.versions[:]:
                            if version[0] == name:
                                sort.versions.remove(version)
                        back = True

        class rule:
            def setup(choice, default, new=True):
                back = False
                while not back:
                    if not new:
                        ui_cls('Options/Settings/Scraper Settings/Versions/Edit')
                        print("Current settings for rule #" + choice + ":")
                        print()
                        print("0) Back")
                        print("1) Edit  attribute : " + default[int(choice) - 1][0])
                        print("2) Edit  weight    : " + default[int(choice) - 1][1])
                        print("3) Edit  operator  : " + default[int(choice) - 1][2])
                        if not default[int(choice) - 1][0] == "cache status" and not default[int(choice) - 1][
                                                                                            2] in ["highest",
                                                                                                "lowest"]:
                            print("4) Edit  value     : " + default[int(choice) - 1][3])
                        print()
                        print(
                            "Choose a value to edit, move this rule by typing 'move' or delete this rule by typing 'remove' ")
                        print()
                        choice2 = input("Choose an action: ")
                    else:
                        ui_cls('Options/Settings/Scraper Settings/Versions/Add')
                        default += [["", "", "", ""]]
                        choice = str(len(default))
                        choice2 = '1'
                    print()
                    if choice2 == '0':
                        back = True
                    elif choice2 == '1':
                        if not new:
                            print("You cannot change the attribute of an existing rule.")
                            print()
                            time.sleep(2)
                        else:
                            print("Please choose an attribute on which this rule should act.")
                            print()
                            indices = []
                            for index, attribute in enumerate(sort.version.rule.__subclasses__()):
                                print(str(index + 1) + ') ' + attribute.name)
                                indices += [str(index + 1)]
                            print()
                            choice3 = input("Please choose an attribute: ")
                            if choice3 in indices:
                                default[int(choice) - 1][int(choice2) - 1] = \
                                sort.version.rule.__subclasses__()[int(choice3) - 1].name
                            choice2 = '2'
                    if choice2 == '2':
                        print(
                            "Please choose a weight for this rule. This rule can either be a requirement or a preference.")
                        print()
                        indices = []
                        for index, attribute in enumerate(sort.version.rule.weights):
                            print(str(index + 1) + ') ' + attribute)
                            indices += [str(index + 1)]
                        print()
                        choice3 = input("Please choose a weight: ")
                        if choice3 in indices:
                            default[int(choice) - 1][int(choice2) - 1] = sort.version.rule.weights[
                                int(choice3) - 1]
                        if new:
                            choice2 = '3'
                    if choice2 == '3':
                        print("Please choose an operator for this rule.")
                        print()
                        operators = []
                        for subclass in sort.version.rule.__subclasses__():
                            if subclass.name == default[int(choice) - 1][0]:
                                operators = subclass.operators
                                break
                        indices = []
                        for index, attribute in enumerate(operators):
                            print(str(index + 1) + ') ' + attribute)
                            indices += [str(index + 1)]
                        print()
                        choice3 = input("Please choose an operator: ")
                        if choice3 in indices:
                            default[int(choice) - 1][int(choice2) - 1] = subclass.operators[int(choice3) - 1]
                        if new and not default[int(choice) - 1][0] == "cache status" and not \
                        default[int(choice) - 1][2] in ["highest", "lowest"]:
                            choice2 = '4'
                        elif new:
                            print("New rule added!")
                            time.sleep(2)
                            new = False
                    if choice2 == '4':
                        working = False
                        for subclass in sort.version.rule.__subclasses__():
                            if subclass.name == default[int(choice) - 1][0]:
                                break
                        while not working:
                            print(
                                "Please choose a value for this rule. Make sure that the value you enter matches your chosen operator.")
                            print()
                            choice3 = input("Please enter a value: ")
                            if subclass.check(choice3):
                                working = True
                        default[int(choice) - 1][int(choice2) - 1] = choice3
                        if new:
                            print("New rule added!")
                            time.sleep(2)
                            new = False
                    if choice2 == 'remove':
                        del default[int(choice) - 1]
                        back = True
                    if choice2 == 'move':
                        print('0) Back')
                        indices = []
                        for i, rule in enumerate(default):
                            print(str(i + 1) + ') Position ' + str(i + 1))
                            indices += [str(i + 1)]
                        print()
                        choice3 = input('Move rule #' + choice + ' to: ')
                        if choice in indices:
                            temp = copy.deepcopy(default[int(choice) - 1])
                            del default[int(choice) - 1]
                            default.insert(int(choice3) - 1, temp)
                            back = True
                    print()

            operators = [""]
            weights = ["requirement", "preference"]

            def __init__(self, attribute, required, operator, value=None) -> None:
                self.attribute = attribute
                self.required = (required == "requirement")
                self.operator = operator
                self.value = value

            def apply(self, scraped_releases: list):
                try:
                    if self.required:
                        if self.operator == "==":
                            for release in scraped_releases[:]:
                                if not getattr(release, self.attribute) == self.value:
                                    scraped_releases.remove(release)
                            return scraped_releases
                        if self.operator == ">=":
                            for release in scraped_releases[:]:
                                if not float(getattr(release, self.attribute)) >= float(self.value):
                                    scraped_releases.remove(release)
                            return scraped_releases
                        if self.operator == "<=":
                            for release in scraped_releases[:]:
                                if not float(getattr(release, self.attribute)) <= float(self.value):
                                    scraped_releases.remove(release)
                            return scraped_releases
                        if self.operator == "highest":
                            scraped_releases.sort(key=lambda s: float(getattr(s, self.attribute)), reverse=True)
                            for release in scraped_releases[:]:
                                if not float(getattr(release, self.attribute)) == float(
                                        getattr(scraped_releases[0], self.attribute)):
                                    scraped_releases.remove(release)
                            return scraped_releases
                        if self.operator == "lowest":
                            scraped_releases.sort(key=lambda s: float(getattr(s, self.attribute)), reverse=False)
                            for release in scraped_releases[:]:
                                if not float(getattr(release, self.attribute)) == float(
                                        getattr(scraped_releases[0], self.attribute)):
                                    scraped_releases.remove(release)
                            return scraped_releases
                        if self.operator == "include":
                            for release in scraped_releases[:]:
                                if not bool(regex.search(self.value, getattr(release, self.attribute), regex.I)):
                                    scraped_releases.remove(release)
                            return scraped_releases
                        if self.operator == "exclude":
                            for release in scraped_releases[:]:
                                if bool(regex.search(self.value, getattr(release, self.attribute), regex.I)):
                                    scraped_releases.remove(release)
                            return scraped_releases
                    else:
                        if self.operator == "==":
                            scraped_releases.sort(key=lambda s: (getattr(s, self.attribute) == self.value),
                                                    reverse=True)
                            return scraped_releases
                        if self.operator == ">=":
                            scraped_releases.sort(
                                key=lambda s: (float(getattr(s, self.attribute)) >= float(self.value)),
                                reverse=True)
                            return scraped_releases
                        if self.operator == "<=":
                            scraped_releases.sort(
                                key=lambda s: (float(getattr(s, self.attribute)) <= float(self.value)),
                                reverse=True)
                            return scraped_releases
                        if self.operator == "highest":
                            scraped_releases.sort(key=lambda s: float(getattr(s, self.attribute)), reverse=True)
                            return scraped_releases
                        if self.operator == "lowest":
                            scraped_releases.sort(key=lambda s: float(getattr(s, self.attribute)), reverse=False)
                            return scraped_releases
                        if self.operator == "include":
                            scraped_releases.sort(
                                key=lambda s: bool(regex.search(self.value, getattr(s, self.attribute), regex.I)),
                                reverse=True)
                            return scraped_releases
                        if self.operator == "exclude":
                            scraped_releases.sort(
                                key=lambda s: bool(regex.search(self.value, getattr(s, self.attribute), regex.I)),
                                reverse=False)
                            return scraped_releases
                except:
                    ui_print("version rule exception - ignoring this rule")
                    return scraped_releases

            def check(self):
                return True

        class resolution(rule):
            name = "resolution"
            operators = ["==", ">=", "<=", "highest", "lowest"]

            def check(self):
                try:
                    float(self)
                    return True
                except:
                    print()
                    print("This value is not in the correct format. Please enter a number (e.g. '420' or '69.69')")
                    print()
                    return False

        class size(rule):
            name = "size"
            operators = ["==", ">=", "<=", "highest", "lowest"]

            def apply(self, scraped_releases: list):
                try:
                    if self.required:
                        if self.operator == "==":
                            for release in scraped_releases[:]:
                                if not getattr(release, self.attribute) == self.value:
                                    scraped_releases.remove(release)
                            return scraped_releases
                        if self.operator == ">=":
                            for release in scraped_releases[:]:
                                if not float(getattr(release, self.attribute)) >= float(self.value):
                                    scraped_releases.remove(release)
                            return scraped_releases
                        if self.operator == "<=":
                            for release in scraped_releases[:]:
                                if not float(getattr(release, self.attribute)) <= float(self.value):
                                    scraped_releases.remove(release)
                            return scraped_releases
                        if self.operator == "highest":
                            scraped_releases.sort(key=lambda s: 5 * round(float(getattr(s, self.attribute)) / 5),
                                                    reverse=True)
                            for release in scraped_releases[:]:
                                if not 5 * round(float(getattr(release, self.attribute)) / 5) == 5 * round(
                                        float(getattr(scraped_releases[0], self.attribute) / 5)):
                                    scraped_releases.remove(release)
                            return scraped_releases
                        if self.operator == "lowest":
                            scraped_releases.sort(key=lambda s: 5 * round(float(getattr(s, self.attribute)) / 5),
                                                    reverse=False)
                            for release in scraped_releases[:]:
                                if not 5 * round(float(getattr(release, self.attribute)) / 5) == 5 * round(
                                        float(getattr(scraped_releases[0], self.attribute)) / 5):
                                    scraped_releases.remove(release)
                            return scraped_releases
                    else:
                        if self.operator == "==":
                            scraped_releases.sort(key=lambda s: (getattr(s, self.attribute) == self.value),
                                                    reverse=True)
                            return scraped_releases
                        if self.operator == ">=":
                            scraped_releases.sort(
                                key=lambda s: (float(getattr(s, self.attribute)) >= float(self.value)),
                                reverse=True)
                            return scraped_releases
                        if self.operator == "<=":
                            scraped_releases.sort(
                                key=lambda s: (float(getattr(s, self.attribute)) <= float(self.value)),
                                reverse=True)
                            return scraped_releases
                        if self.operator == "highest":
                            scraped_releases.sort(key=lambda s: 5 * round(float(getattr(s, self.attribute)) / 5),
                                                    reverse=True)
                            return scraped_releases
                        if self.operator == "lowest":
                            scraped_releases.sort(key=lambda s: 5 * round(float(getattr(s, self.attribute)) / 5),
                                                    reverse=False)
                            return scraped_releases
                except:
                    ui_print("version rule exception - ignoring this rule")
                    return scraped_releases

            def check(self):
                try:
                    float(self)
                    return True
                except:
                    print()
                    print("This value is not in the correct format. Please enter a number (e.g. '420' or '69.69')")
                    print()
                    return False

        class seeders(rule):
            name = "seeders"
            operators = ["==", ">=", "<=", "highest", "lowest"]

            def check(self):
                try:
                    float(self)
                    return True
                except:
                    print()
                    print("This value is not in the correct format. Please enter a number (e.g. '420' or '69.69')")
                    print()
                    return False

        class title(rule):
            name = "title"
            operators = ["==", "include", "exclude"]

            def check(self):
                try:
                    regex.search(self, self, regex.I)
                    return True
                except:
                    print()
                    print(
                        "This value is not in the correct format. Please make sure this value is a valid regex expression and no characters are escaped accidentally.")
                    print()
                    return False

        class source(rule):
            name = "source"
            operators = ["==", "include", "exclude"]

            def check(self):
                try:
                    regex.search(self, self, regex.I)
                    return True
                except:
                    print()
                    print(
                        "This value is not in the correct format. Please make sure this value is a valid regex expression and no characters are escaped accidentally.")
                    print()
                    return False

        class cache_status(rule):
            name = "cache status"
            operators = ["cached", "uncached"]

            def __init__(self, attribute, required, operator, value=None) -> None:
                self.attribute = "cached"
                self.required = (required == "requirement")
                self.operator = operator
                self.value = value

            def apply(self, scraped_releases: list):
                try:
                    if self.required:
                        if self.operator == "cached":
                            for release in scraped_releases[:]:
                                if len(getattr(release, self.attribute)) == 0:
                                    scraped_releases.remove(release)
                            return scraped_releases
                        if self.operator == "uncached":
                            for release in scraped_releases[:]:
                                if len(getattr(release, self.attribute)) > 0:
                                    scraped_releases.remove(release)
                            return scraped_releases
                    else:
                        if self.operator == "cached":
                            scraped_releases.sort(key=lambda s: len(getattr(s, self.attribute)), reverse=True)
                            return scraped_releases
                        if self.operator == "uncached":
                            scraped_releases.sort(key=lambda s: len(getattr(s, self.attribute)), reverse=False)
                            return scraped_releases
                except:
                    ui_print("version rule exception - ignoring this rule")
                    return scraped_releases

        def __init__(self, name, media, required, rules) -> None:
            self.name = name
            self.media = media
            self.required = required
            self.rules = rules

    unwanted = ['sample']
    versions = [
        ["2160p SDR", "both", "true", [
            ["cache status", "requirement", "cached", ""],
            ["resolution", "requirement", ">=", "2160"],
            ["title", "requirement", "exclude", "(\.DV\.|\.3D\.|\.H?D?.?CAM\.)"],
            ["title", "preference", "exclude", "(\.HDR\.)"],
            ["title", "preference", "include", "(EXTENDED|REMASTERED)"],
            ["size", "preference", "lowest", ""],
            ["seeders", "preference", "highest", ""],
            ["size", "requirement", ">=", "0.1"],
        ]],
        ["1080p SDR", "both", "true", [
            ["cache status", "requirement", "cached", ""],
            ["resolution", "requirement", "<=", "1080"],
            ["resolution", "preference", "highest", ""],
            ["title", "requirement", "exclude", "(\.DV\.|\.3D\.|\.H?D?.?CAM\.)"],
            ["title", "requirement", "exclude", "(\.HDR\.)"],
            ["title", "preference", "include", "(EXTENDED|REMASTERED)"],
            ["size", "preference", "lowest", ""],
            ["seeders", "preference", "highest", ""],
            ["size", "requirement", ">=", "0.1"],
        ]],
    ]
    always_on_rules = [version.rule("wanted", "preference", "highest", ""),
                        version.rule("unwanted", "preference", "lowest", "")]

    def __new__(self, scraped_releases: list, version: version):
        if len(scraped_releases) > 0:
            for rule in reversed(sort.always_on_rules):
                rule.apply(scraped_releases)
            for rule in reversed(version.rules):
                for subrule in sort.version.rule.__subclasses__():
                    if subrule.name == rule[0]:
                        rule = subrule(rule[0], rule[1], rule[2], rule[3])
                        break
                scraped_releases = rule.apply(scraped_releases)
            ui_print('sorting releases for version [' + version.name + '] ... done - found ' + str(
                len(scraped_releases)) + ' releases')
        return scraped_releases

class torrent2magnet:
    class BTFailure(Exception):
        pass

    def decode_int(x, f):
        f += 1
        newf = x.find(b"e", f)
        n = int(x[f:newf])
        if six.indexbytes(x, f) == 45:
            if six.indexbytes(x, f + 1) == 48:
                raise ValueError
        elif six.indexbytes(x, f) == 48 and newf != f + 1:
            raise ValueError
        return (n, newf + 1)

    def decode_string(x, f):
        colon = x.find(b":", f)
        n = int(x[f:colon])
        if six.indexbytes(x, f) == 48 and colon != f + 1:
            raise ValueError
        colon += 1
        return (x[colon: colon + n], colon + n)

    def decode_list(x, f):
        r, f = [], f + 1
        while six.indexbytes(x, f) != 101:
            v, f = torrent2magnet.decode_func[six.indexbytes(x, f)](x, f)
            r.append(v)
        return (r, f + 1)

    def decode_dict(x, f):
        r, f = {}, f + 1
        while six.indexbytes(x, f) != 101:
            k, f = torrent2magnet.decode_string(x, f)
            r[k], f = torrent2magnet.decode_func[six.indexbytes(x, f)](x, f)
        return (r, f + 1)

    decode_func = {}
    decode_func[108] = decode_list
    decode_func[100] = decode_dict
    decode_func[105] = decode_int
    for i in range(48, 59):
        decode_func[i] = decode_string

    def bdecode(x):
        try:
            r, l = torrent2magnet.decode_func[six.indexbytes(x, 0)](x, 0)
        except (IndexError, KeyError, ValueError):
            raise
            raise BTFailure("not a valid bencoded string")
        if l != len(x):
            raise torrent2magnet.BTFailure("invalid bencoded value (data after valid prefix)")
        return r

    class Bencached(object):
        __slots__ = ["bencoded"]

        def __init__(self, s):
            self.bencoded = s

    def encode_bencached(x, r):
        r.append(x.bencoded)

    def encode_int(x, r):
        r.extend((b"i", str(x).encode(), b"e"))

    def encode_bool(x, r):
        if x:
            torrent2magnet.encode_int(1, r)
        else:
            torrent2magnet.encode_int(0, r)

    def encode_string(x, r):
        r.extend((str(len(x)).encode(), b":", x))

    def encode_list(x, r):
        r.append(b"l")
        for i in x:
            torrent2magnet.encode_func[type(i)](i, r)
        r.append(b"e")

    def encode_dict(x, r):
        r.append(b"d")
        for k, v in sorted(x.items()):
            r.extend((str(len(k)).encode(), b":", k))
            torrent2magnet.encode_func[type(v)](v, r)
        r.append(b"e")

    encode_func = {}
    encode_func[Bencached] = encode_bencached
    encode_func[int] = encode_int
    encode_func[str] = encode_string
    encode_func[bytes] = encode_string
    encode_func[list] = encode_list
    encode_func[tuple] = encode_list
    encode_func[dict] = encode_dict

    def bencode(x):
        r = []
        torrent2magnet.encode_func[type(x)](x, r)
        return b"".join(r)

    def __new__(cls, x):
        metadata = torrent2magnet.bdecode(x)
        subj = metadata[b'info']
        hashcontents = torrent2magnet.bencode(subj)
        digest = hashlib.sha1(hashcontents).hexdigest()
        return 'magnet:?' \
                + 'xt=urn:btih:' + digest \
                + '&dn=' + metadata[b'info'][b'name'].decode() \
                + '&tr=' + metadata[b'announce'].decode() 

def print_releases(scraped_releases):
    longest_file = 0
    longest_cached = 0
    longest_title = 0
    longest_size = 0
    longest_index = 0
    longest_seeders = 0
    for index, release in enumerate(scraped_releases):
        release.printsize = str(round(release.size, 2))
        release.file = '+' + str(release.wanted) + '/-' + str(release.unwanted)
        if len(release.file) > longest_file:
            longest_file = len(release.file)
        if len('/'.join(release.cached)) > longest_cached:
            longest_cached = len('/'.join(release.cached))
        if len(release.title) > longest_title:
            longest_title = len(release.title)
        if len(str(release.printsize)) > longest_size:
            longest_size = len(str(release.printsize))
        if len(str(release.seeders)) > longest_seeders:
            longest_seeders = len(str(release.seeders))
        if len(str(index + 1)) > longest_index:
            longest_index = len(str(index + 1))
    for index, release in enumerate(scraped_releases):
        print(str(index + 1) + ") " + ' ' * (
                    longest_index - len(str(index + 1))) + "title: " + release.title + ' ' * (
                            longest_title - len(release.title)) + " | size: " + str(release.printsize) + ' ' * (
                            longest_size - len(str(release.printsize))) + " | cached: " + '/'.join(
            release.cached) + ' ' * (longest_cached - len('/'.join(release.cached))) + " | seeders: " + str(
            release.seeders) + ' ' * (
                            longest_seeders - len(str(release.seeders))) + " | files: " + release.file + ' ' * (
                            longest_file - len(release.file)) + " | source: " + release.source)
