from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment


ROOT = Path(__file__).resolve().parent.parent
PRINT_FORMAT_ROOT = ROOT / "print_pro" / "print_pro" / "print_format"
SAMPLE_ROOT = ROOT / "preview_samples"
OUTPUT_ROOT = ROOT / "preview_output"


def wrap(value: Any) -> Any:
	if isinstance(value, dict):
		return AttrDoc(value)
	if isinstance(value, list):
		return [wrap(item) for item in value]
	return value


class AttrDoc:
	def __init__(self, data: dict[str, Any]):
		object.__setattr__(self, "_data", {key: wrap(value) for key, value in data.items()})

	def __getattr__(self, item: str) -> Any:
		data = object.__getattribute__(self, "_data")
		if item in data:
			return data[item]
		raise AttributeError(item)

	def __setattr__(self, key: str, value: Any) -> None:
		object.__getattribute__(self, "_data")[key] = wrap(value)

	def __getitem__(self, key: str) -> Any:
		return object.__getattribute__(self, "_data")[key]

	def get(self, key: str, default: Any = None) -> Any:
		return object.__getattribute__(self, "_data").get(key, default)

	def get_formatted(self, fieldname: str, child: Any | None = None) -> str:
		target = child if child is not None else self
		if isinstance(target, AttrDoc):
			value = target.get(fieldname)
		else:
			value = getattr(target, fieldname, None)
		return format_value(value)


def format_value(value: Any) -> str:
	if value in (None, ""):
		return ""
	if isinstance(value, (int, float)):
		return f"{value:,.2f}"
	if isinstance(value, str):
		if looks_like_date(value):
			return format_date_string(value)
		return value
	if isinstance(value, date):
		return value.strftime("%m/%d/%Y")
	if isinstance(value, datetime):
		return value.strftime("%m/%d/%Y")
	return str(value)


def looks_like_date(value: str) -> bool:
	return len(value) == 10 and value[4] == "-" and value[7] == "-"


def format_date_string(value: str) -> str:
	try:
		parsed = datetime.strptime(value, "%Y-%m-%d")
	except ValueError:
		return value
	return parsed.strftime("%m/%d/%Y")


@dataclass
class FakeDB:
	values: dict[tuple[str, str, str], Any]

	def get_value(self, doctype: str, name: str, fieldname: str) -> Any:
		return self.values.get((doctype, name, fieldname), "")


class FakeFrappe:
	def __init__(self, linked_docs: dict[str, dict[str, Any]], db_values: dict[tuple[str, str, str], Any]):
		self.linked_docs = linked_docs
		self.db = FakeDB(db_values)

	def get_doc(self, doctype: str, name: str) -> Any:
		"""Return wrapped linked doc, or None if not found (templates use `if lh` guards)."""
		doc = self.linked_docs.get(doctype, {}).get(name)
		if doc is None:
			return None
		return wrap(doc)

	def get_all(
		self,
		doctype: str,
		filters: dict[str, Any] | None = None,
		fields: list[str] | None = None,
		limit: int = 20,
		**kwargs: Any,
	) -> list[Any]:
		"""Return all linked docs for a doctype that match the given filters."""
		docs = self.linked_docs.get(doctype, {})
		results = []
		for name, data in docs.items():
			row = dict(data)
			row.setdefault("name", name)
			# apply simple equality filters
			if filters:
				if not all(row.get(k) == v for k, v in filters.items()):
					continue
			# keep only requested fields
			if fields:
				row = {f: row.get(f) for f in fields}
			results.append(wrap(row))
			if len(results) >= limit:
				break
		return results

	def get_cached_value(self, doctype: str, name: str, fieldname: str) -> Any:
		"""Delegate to db.get_value for local preview."""
		return self.db.get_value(doctype, name, fieldname)


def load_sample_data(print_format_name: str) -> dict[str, Any]:
	sample_path = SAMPLE_ROOT / f"{print_format_name}.json"
	if not sample_path.exists():
		raise FileNotFoundError(f"Missing sample file: {sample_path}")
	return json.loads(sample_path.read_text(encoding="utf-8"))


def list_print_formats() -> list[str]:
	return sorted(
		path.name
		for path in PRINT_FORMAT_ROOT.iterdir()
		if path.is_dir() and (path / f"{path.name}.html").exists()
	)


def make_context(sample_data: dict[str, Any]) -> dict[str, Any]:
	doc = wrap(sample_data["doc"])
	linked_docs = sample_data.get("linked_docs", {})
	raw_db_values = sample_data.get("db_values", {})
	db_values = {}
	for key, value in raw_db_values.items():
		doctype, name, fieldname = key.split("::", 2)
		db_values[(doctype, name, fieldname)] = value
	frappe = FakeFrappe(linked_docs, db_values)
	return {"doc": doc, "frappe": frappe}


def render_print_format(print_format_name: str) -> Path:
	template_path = PRINT_FORMAT_ROOT / print_format_name / f"{print_format_name}.html"
	if not template_path.exists():
		raise FileNotFoundError(f"Missing template: {template_path}")

	sample_data = load_sample_data(print_format_name)
	context = make_context(sample_data)

	env = Environment()
	template = env.from_string(template_path.read_text(encoding="utf-8"))
	rendered = template.render(**context)

	OUTPUT_ROOT.mkdir(exist_ok=True)
	output_path = OUTPUT_ROOT / f"{print_format_name}.preview.html"
	output_path.write_text(rendered, encoding="utf-8")
	return output_path


def render_many(print_format_names: list[str]) -> list[Path]:
	return [render_print_format(name) for name in print_format_names]


def main() -> None:
	parser = argparse.ArgumentParser(description="Render a local preview for a Frappe print format.")
	parser.add_argument("print_format_name", nargs="?", help="Folder name of the print format, e.g. corporate_blue_invoice")
	parser.add_argument("--all", action="store_true", help="Render previews for every print format that has a sample JSON file.")
	parser.add_argument("--list", action="store_true", help="List available print format folders.")
	args = parser.parse_args()

	if args.list:
		for name in list_print_formats():
			print(name)
		return

	if args.all:
		available = []
		for name in list_print_formats():
			if (SAMPLE_ROOT / f"{name}.json").exists():
				available.append(name)
		for output_path in render_many(available):
			print(output_path)
		return

	if not args.print_format_name:
		parser.error("Provide a print format name, or use --all / --list.")

	output_path = render_print_format(args.print_format_name)
	print(output_path)


if __name__ == "__main__":
	main()
