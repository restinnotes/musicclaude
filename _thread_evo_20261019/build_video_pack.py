"""Package accepted line-and-bead documents and a source-quoted video introduction."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
import covjudge

ROOT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def introduction(tag):
    """Extract existing descriptions verbatim; keep provenance outside the ZIP too."""
    selections = [
        ('要做什么', '标准.md',
         '一首器乐作品“边听边读”的视频文字里，**线**是一个人在这首曲子里经历的一件事，作用是把逐段的听感记录（**珠子**）串成一个整体。最后线的每条要点后面跟着它串起的珠子，读者顺着读下去，不用来回跳。'),
        ('希望读起来是什么感觉', '标准.md',
         '- 只读线、不看珠子，它自己就是一件有逻辑、有时序、内在有发展的事，各段不是各说各的。'),
        ('希望读起来是什么感觉', '标准.md',
         '- 像一个人平平常常讲自己的经历。讲的是心理，但用平常话讲，读者不用自己去提炼；不是心理分析，也不是哲理。'),
        ('视频文字怎样组织', '标准.md',
         '- 按音乐段落分段，每段 2–4 条要点，每条是一句完整、自然的话；分条是为了每条只说一件事、之后做视频好挑好排，连着读仍要像一段流畅的经历。'),
        ('时长与观看方式', 'THREAD_SPEC.md',
         '1. **时长就是音乐的时长**；观众可以来回看、反复看。**不能为了时长牺牲视频本身的内容价值**；需要的话可以分多个版本。'),
    ]
    lines = ['# 视频介绍（已有材料原文摘录）', '',
             f'文字素材版本：`{tag}`。本说明摘录现有项目材料及本聊天用户原话；每段附来源。', '']
    provenance = []
    previous = None
    for heading, relative, quote in selections:
        source = ROOT / relative
        original = source.read_text(encoding='utf-8')
        assert original.count(quote) == 1, f'Introduction source changed or ambiguous: {relative}'
        line_number = original[:original.index(quote)].count('\n') + 1
        if heading != previous:
            lines += [f'## {heading}', '']
            previous = heading
        lines += ['> ' + quote, '', f'出处：`{relative}`，第 {line_number} 行。', '']
        provenance.append({'heading': heading, 'source': str(source), 'line': line_number,
                           'source_text_sha256': sha(original.encode('utf-8')),
                           'quote': quote, 'verbatim_verified': True})
    quote = '这样能让组织更明确 就比如之后在画面上 我们就可以使用比如同一种颜色 或者相近的颜色来进行暗示说这个线在串起来这些珠子'
    source = '本聊天用户原话：提出“珠子的哪一部分对应上线说的是哪一部分”功能的消息。'
    lines += ['## 片段对应与配色设想', '', '> ' + quote, '', f'出处：{source}', '',
              f'此处摘录的是后续画面呈现设想。本包的 {tag} 文字素材未附逐片段配色标注。', '',
              '## 本包文字素材', '',
              f'- [Op.60：线与珠子](op60_线与珠子_{tag}.md)',
              f'- [Op.61：线与珠子](op61_线与珠子_{tag}.md)', '']
    provenance.append({'heading': '片段对应与配色设想', 'source': source,
                       'quote': quote, 'source_kind': 'user_message_in_current_chat'})
    # Keep this support file outside deliver_*_TAG, whose accepted delivery is unique.
    document = ROOT / 'video_pack_notes' / tag / '00_视频介绍.md'
    document.parent.mkdir(parents=True, exist_ok=True)
    data = ('\n'.join(lines)).encode('utf-8')
    document.write_bytes(data)
    return document, data, provenance


def build(tag):
    if not tag or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in tag):
        raise ValueError('Invalid version tag')
    folders = [p for p in ROOT.glob(f'deliver_*_{tag}') if p.is_dir()]
    if len(folders) != 1:
        raise ValueError('An unambiguous accepted delivery is required')
    folder = folders[0]
    integrity = json.loads((folder / 'integrity.json').read_text(encoding='utf-8'))
    accepted = ROOT / 'runs/_batches/round50_from_r49b' / f'{tag}_acceptance.json'
    receipt = json.loads(accepted.read_text(encoding='utf-8'))
    assert receipt['tag'] == tag and receipt['fair']['pass'] and receipt['floor']['status'] == 'pass'
    intro_document, intro_data, intro_sources = introduction(tag)
    sources = [(intro_document, intro_data)]
    for work in ('op60', 'op61'):
        graph_file = ROOT / 'evaluations/v6fix' / f'{work}_{tag}.json'
        # Acceptance records use read_text(), which normalizes Windows CRLF.
        assert sha(graph_file.read_text(encoding='utf-8').encode('utf-8')) == integrity[work]['source_sha256'], 'Accepted graph changed'
        document = folder / f'{work}_线与珠子_{tag}.md'
        data = document.read_bytes()
        text = data.decode('utf-8')
        graph = json.loads(graph_file.read_text(encoding='utf-8'))['graph']
        assert all(text.count(i['text']) == 1 for s in graph['segments'] for i in s['items'])
        beads = [b for b in covjudge.beads(work) if b['role'] != '演奏条件']
        for name in ('beads_clean', 'beads_lang'):
            overlay = ROOT / 'evaluations' / name / f'{work}.json'
            if overlay.exists():
                replacements = json.loads(overlay.read_text(encoding='utf-8'))
                beads = [dict(b, text=replacements.get(b['id'], b['text'])) for b in beads]
        assert len(beads) == integrity[work]['珠子数']
        assert all(text.count(b['text']) == 1 for b in beads), 'Immutable display bead missing or changed'
        assert '**Center：**' in text and '小节' in text and '> ' in text
        assert integrity[work]['珠子逐字一致'] and integrity[work]['线逐字在合写内']
        sources.append((document, data))
    target = ROOT / f'视频最小包_{tag}.zip'
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for document, data in sources:
            info = zipfile.ZipInfo(document.name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=9)
    with zipfile.ZipFile(target) as archive:
        assert archive.namelist() == [p.name for p, _ in sources]
        assert archive.testzip() is None
        assert all(archive.read(p.name) == data for p, data in sources), 'Package changed document bytes'
    proof = {'tag': tag, 'accepted_receipt': str(accepted.relative_to(ROOT)),
             'files': [{'name': p.name, 'source': str(p.relative_to(ROOT)), 'sha256': sha(data)} for p, data in sources],
             'zip': str(target), 'zip_sha256': sha(target.read_bytes()), 'bytes': target.stat().st_size,
             'file_count': len(sources), 'unzip_bytes_identical': True,
             'introduction_sources': intro_sources,
             'contents': 'Source-quoted video introduction and two accepted joined documents; measure ranges, line text, immutable display beads and per-item arrangement. No older span offsets.'}
    audit = ROOT / 'runs/_reports' / f'video_pack_{tag}.json'
    audit.parent.mkdir(parents=True, exist_ok=True)
    audit.write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(proof, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tag')
    build(parser.parse_args().tag)
