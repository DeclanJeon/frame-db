"""Apply a fully verified Drive mirror to an in-memory seed before it is saved."""
import hashlib
import json
import re
from typing import TypedDict


class DriveFile(TypedDict):
    asset_id: str
    file_id: str
    source_url: str
    bytes: int
    sha256: str


class DriveManifest(TypedDict):
    root_folder_id: str
    files: list[DriveFile]


class TransferCheck(TypedDict):
    file_id: str
    ok: bool
    bytes: int
    sha256: str


class TransferAudit(TypedDict):
    total: int
    passed: int
    failed: list[TransferCheck]
    files: list[TransferCheck]


class Reference(TypedDict):
    id: str
    source: str
    resources: dict[str, str]
    thumbnail_url: str
    display_url: str


class Media(TypedDict):
    entry_id: str
    variant_id: str
    source_id: str
    original_id: str
    availability: str
    url: str


class Variant(TypedDict):
    id: str
    attributes: str


class Entry(TypedDict):
    id: str
    details: str


class Source(TypedDict):
    id: str
    hosting: str


class ImportBatch(TypedDict):
    source_id: str
    report: str


class Seed(TypedDict):
    entries: list[Entry]
    variants: list[Variant]
    media_assets: list[Media]
    sources: list[Source]
    import_batches: list[ImportBatch]


class DriveManifestError(ValueError):
    def __init__(self, issue: str) -> None:
        self.issue = issue
        super().__init__(issue)


def apply_drive(seed: Seed, references: list[Reference], manifest: DriveManifest,
                audit: TransferAudit) -> None:
    """Mutate the seed only after every source representation passes the audit."""
    files = manifest['files']
    required = {url for reference in references for url in reference['resources'].values()}
    required.update(media['url'] for media in seed['media_assets'])
    by_url = {file['source_url']: file for file in files}
    if set(by_url) != required or len(by_url) != len(files):
        raise DriveManifestError('Drive manifest does not cover the exact source resources')
    if len({file['asset_id'] for file in files}) != len(files) or len({file['file_id'] for file in files}) != len(files):
        raise DriveManifestError('Drive manifest contains aliased file or asset IDs')
    checks = {check['file_id']: check for check in audit['files']}
    if audit['total'] != len(files) or audit['passed'] != len(files) or audit['failed'] or len(checks) != len(files):
        raise DriveManifestError('Drive transfer audit is incomplete')
    for file in files:
        expected_id = hashlib.sha256(file['source_url'].encode()).hexdigest()[:24]
        check = checks.get(file['file_id'])
        if file['asset_id'] != expected_id or not re.fullmatch(r'[\w-]{20,}', file['file_id']):
            raise DriveManifestError('Drive file identity is invalid')
        if not check or not check['ok'] or check['sha256'] != file['sha256'] or check['bytes'] != file['bytes']:
            raise DriveManifestError('Drive file bytes have not been verified')
    variants = {variant['id']: variant for variant in seed['variants']}
    entries = {entry['id']: entry for entry in seed['entries']}
    if any(media['variant_id'] not in variants or media['entry_id'] not in entries for media in seed['media_assets']):
        raise DriveManifestError('Seed media has an unresolved entry or variant')

    references_by_id = {reference['id']: reference for reference in references}
    details_by_id = {entry['id']: json.loads(entry['details']) for entry in seed['entries']}
    for media in seed['media_assets']:
        original = media['url']
        file = by_url[original]
        reference = references_by_id.get(media['original_id'])
        thumbnail = reference['thumbnail_url'] if reference else original
        display = reference['display_url'] if reference else original
        variant = variants[media['variant_id']]
        attributes = json.loads(variant['attributes'])
        attributes.update(
            original_url=original,
            thumbnail_url='/api/media/' + by_url[thumbnail]['asset_id'],
            display_url='/api/media/' + by_url[display]['asset_id'],
            drive_file_id=file['file_id'],
        )
        variant['attributes'] = json.dumps(attributes, ensure_ascii=False)
        media['url'] = '/api/media/' + file['asset_id']
        if media['availability'] == 'external_link':
            media['availability'] = 'google_drive'
        details_by_id[media['entry_id']].setdefault('Drive 리소스', []).append({
            'id': media['original_id'], '썸네일': attributes['thumbnail_url'],
            '표시용': attributes['display_url'], '원본': media['url'],
        })
    for entry in seed['entries']:
        entry['details'] = json.dumps(details_by_id[entry['id']], ensure_ascii=False)
    hosted_sources = {media['source_id'] for media in seed['media_assets']}
    for source in seed['sources']:
        if source['id'] in hosted_sources:
            source['hosting'] = 'google_drive'
    for batch in seed['import_batches']:
        source = batch['source_id'].removesuffix('-db')
        urls = {url for reference in references if reference['source'] == source for url in reference['resources'].values()}
        report = json.loads(batch['report'])
        report.update(media_downloaded=sum(reference['source'] == source for reference in references),
                      drive_representations=len(urls), drive_verified=True,
                      drive_root_folder_id=manifest['root_folder_id'])
        batch['report'] = json.dumps(report, ensure_ascii=False)
