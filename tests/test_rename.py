from app.services.rename import RenameService

def test_local_parser():
    p=RenameService().parse_local("Example.Title.S02E03.1080p.x265.mkv")
    assert p.season == 2
    assert p.episode == 3
    assert p.resolution.lower() == "1080p"
    assert p.codec.lower() == "x265"

def test_render():
    s=RenameService()
    p=s.parse_local("Example.S01E02.720p.mkv")
    out=s.render(p,"{title} - S{season:02d}E{episode:02d} - {resolution}")
    assert "S01E02" in out
