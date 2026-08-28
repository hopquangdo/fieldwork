from bts_organizer.domain.naming import dot_key, looks_like_blueprint_name, mong_key, parse


def test_parse_component():
    c = parse("Ma ní đầu trên Tầng dây 1@ 9@40@38@--1--.jpg")
    assert c is not None and c.is_primary and c.ts == (9, 40, 38)
    assert "ma ní đầu trên tầng dây 1" == c.prefix


def test_parse_timestamp_only_is_none():
    assert parse("@9@40@38@--0--.jpg") is None
    assert parse("  @ 9 @ 40 @ 38 @--0--.jpg") is None


def test_component_keys():
    assert mong_key(parse("Móng M4@1@2@3@--0--.jpg").prefix) == "M4"
    assert dot_key(parse("Đốt D6@1@2@3@--0--.jpg").prefix) == 6
    assert mong_key("chân cột") is None


def test_blueprint_name_signal():
    assert looks_like_blueprint_name(parse("Móng M0@1@2@3@--0--.jpg").prefix)
    assert not looks_like_blueprint_name("móng m2")
