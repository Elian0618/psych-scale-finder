/*
Use these standalone CNKI fast-path functions with
mcp__chrome_devtools__evaluate_script. Copy one function body into the tool
call after replacing config placeholders such as YOUR_KEYWORDS or FORMAT.

These helpers intentionally avoid relying on external cnki-* skills.
*/

const cnkiBasicSearch = async () => {
  const query = "YOUR_KEYWORDS";
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const visible = (el) => {
    if (!el) return false;
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== "none" &&
      style.visibility !== "hidden" &&
      Number(style.opacity || 1) > 0 &&
      rect.width > 0 &&
      rect.height > 0 &&
      rect.bottom > 0 &&
      rect.top < innerHeight;
  };
  const waitFor = async (predicate, label, timeoutMs = 60000) => {
    const started = Date.now();
    while (Date.now() - started < timeoutMs) {
      if (predicate()) return true;
      await sleep(500);
    }
    throw new Error(label);
  };

  try {
    await waitFor(
      () => document.querySelector("input.search-input") && document.querySelector("input.search-btn"),
      "search_input_not_ready"
    );
    if (visible(document.querySelector("#tcaptcha_transform_dy"))) {
      return { error: "cnki_captcha", message: "CNKI captcha is visible.", url: location.href };
    }

    const input = document.querySelector("input.search-input");
    const button = document.querySelector("input.search-btn");
    if (!input || !button) {
      return { error: "cnki_selector_changed", message: "Search input/button not found.", url: location.href };
    }

    input.focus();
    input.value = query;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
    button.click();

    await waitFor(() => /条结果|未找到|无结果/.test(document.body?.innerText || ""), "search_results_not_ready");
    if (visible(document.querySelector("#tcaptcha_transform_dy"))) {
      return { error: "cnki_captcha", message: "CNKI captcha appeared after search submit.", url: location.href };
    }

    const rows = document.querySelectorAll(".result-table-list tbody tr");
    const checkboxes = document.querySelectorAll(".result-table-list tbody input.cbItem");
    const totalText = document.querySelector(".pagerTitleCell")?.innerText || "";
    const total = totalText.match(/([\d,]+)/)?.[1] || "0";
    const page = document.querySelector(".countPageMark")?.innerText || "1/1";

    const results = Array.from(rows).map((row, i) => {
      const titleLink = row.querySelector("td.name a.fz14");
      const authors = Array.from(row.querySelectorAll("td.author a.KnowledgeNetLink") || [])
        .map((a) => a.innerText?.trim())
        .filter(Boolean);
      return {
        n: i + 1,
        title: titleLink?.innerText?.trim() || "",
        href: titleLink?.href || "",
        exportId: checkboxes[i]?.value || "",
        authors: authors.join("; "),
        source: row.querySelector("td.source a")?.innerText?.trim() || "",
        database: row.querySelector("td.data")?.innerText?.trim() || "",
        date: row.querySelector("td.date")?.innerText?.trim() || "",
        citations: row.querySelector("td.quote")?.innerText?.trim() || "",
        downloads: row.querySelector("td.download")?.innerText?.trim() || "",
      };
    });

    return {
      status: rows.length ? "cnki_ready" : total === "0" ? "cnki_no_results" : "cnki_selector_changed",
      query,
      total,
      page,
      results,
      url: location.href,
      bodyHint: rows.length ? "" : (document.body?.innerText || "").slice(0, 500),
    };
  } catch (error) {
    return {
      error: "cnki_page_not_ready",
      message: String(error && error.message ? error.message : error),
      query,
      title: document.title,
      url: location.href,
      bodyHint: (document.body?.innerText || "").slice(0, 500),
    };
  }
};

const cnkiPaperDetail = async () => {
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const visible = (el) => {
    if (!el) return false;
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== "none" &&
      style.visibility !== "hidden" &&
      Number(style.opacity || 1) > 0 &&
      rect.width > 0 &&
      rect.height > 0 &&
      rect.bottom > 0 &&
      rect.top < innerHeight;
  };
  const waitFor = async (predicate, label, timeoutMs = 60000) => {
    const started = Date.now();
    while (Date.now() - started < timeoutMs) {
      if (predicate()) return true;
      await sleep(500);
    }
    throw new Error(label);
  };

  try {
    await waitFor(
      () => document.querySelector(".brief") || /摘要|关键词|下载/.test(document.body?.innerText || ""),
      "detail_page_not_ready"
    );
    if (visible(document.querySelector("#tcaptcha_transform_dy"))) {
      return { error: "cnki_captcha", message: "CNKI captcha is visible.", url: location.href };
    }

    const brief = document.querySelector(".brief");
    if (!brief) {
      return { error: "cnki_selector_changed", message: "Paper detail section not found.", url: location.href };
    }

    const title = brief.querySelector("h1")?.innerText?.trim()
      ?.replace(/\s*附视频\s*$/, "")
      ?.replace(/\s*网络首发\s*$/, "") || "";
    const authorH3s = brief.querySelectorAll("h3.author");
    const authors = Array.from(authorH3s[0]?.querySelectorAll("a") || []).map((a) => {
      const text = a.innerText || "";
      const supMatch = text.match(/(\d+)$/);
      return { name: text.replace(/\d+$/, "").trim(), affiliationNum: supMatch ? supMatch[1] : "" };
    });
    const affiliations = Array.from(authorH3s[1]?.querySelectorAll("a") || []).map((a) => a.innerText?.trim() || "");
    const keywords = document.querySelector("p.keywords")
      ? Array.from(document.querySelectorAll("p.keywords a")).map((a) => a.innerText?.replace(/;$/, "").trim()).filter(Boolean)
      : [];

    return {
      status: "cnki_ready",
      title,
      authors,
      affiliations,
      abstract: document.querySelector(".abstract-text")?.innerText?.trim() || "",
      keywords,
      fund: document.querySelector("p.funds")?.innerText?.trim() || "",
      classification: document.querySelector(".clc-code")?.innerText?.trim() || "",
      source: document.querySelector(".doc-top a")?.innerText?.trim() || "",
      pubInfo: document.querySelector(".head-time")?.innerText?.trim() || "",
      toc: document.querySelector(".catalog-list, .catalog-listDiv")?.innerText?.trim() || "",
      hasPDF: !!(document.querySelector("#pdfDown") || document.querySelector(".btn-dlpdf a")),
      hasCAJ: !!(document.querySelector("#cajDown") || document.querySelector(".btn-dlcaj a")),
      url: location.href,
    };
  } catch (error) {
    return {
      error: "cnki_page_not_ready",
      message: String(error && error.message ? error.message : error),
      title: document.title,
      url: location.href,
      bodyHint: (document.body?.innerText || "").slice(0, 500),
    };
  }
};

const cnkiDirectDownload = async () => {
  const format = "FORMAT"; // "pdf", "caj", or "" for automatic preference.
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const visible = (el) => {
    if (!el) return false;
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== "none" &&
      style.visibility !== "hidden" &&
      Number(style.opacity || 1) > 0 &&
      rect.width > 0 &&
      rect.height > 0 &&
      rect.bottom > 0 &&
      rect.top < innerHeight;
  };
  const waitFor = async (predicate, label, timeoutMs = 60000) => {
    const started = Date.now();
    while (Date.now() - started < timeoutMs) {
      if (predicate()) return true;
      await sleep(500);
    }
    throw new Error(label);
  };

  try {
    await waitFor(
      () => document.querySelector(".brief h1") || /下载|摘要|关键词/.test(document.body?.innerText || ""),
      "detail_page_not_ready"
    );
    const title = document.querySelector(".brief h1")?.innerText?.trim()
      ?.replace(/\s*附视频\s*$/, "")
      ?.replace(/\s*网络首发\s*$/, "") || document.title;
    if (visible(document.querySelector("#tcaptcha_transform_dy"))) {
      return { error: "cnki_captcha", message: "CNKI captcha is visible.", title, url: location.href };
    }

    const bodyText = document.body?.innerText || "";
    const pdfLink = document.querySelector("#pdfDown") || document.querySelector(".btn-dlpdf a");
    const cajLink = document.querySelector("#cajDown") || document.querySelector(".btn-dlcaj a");
    const notLogged = document.querySelector(".downloadlink.icon-notlogged") || document.querySelector('[class*="notlogged"]');
    if (notLogged || (/请先登录/.test(bodyText) && !pdfLink && !cajLink)) {
      return { error: "cnki_login_needed", message: "Download requires CNKI login.", title, url: location.href };
    }
    if (/没有权限|暂无权限|未订购|机构未订购|购买|充值/.test(bodyText) && !pdfLink && !cajLink) {
      return { error: "cnki_access_blocked", message: "No institutional/download access detected.", title, url: location.href };
    }

    let selected = null;
    let selectedFormat = "";
    if (format === "pdf" && pdfLink) {
      selected = pdfLink;
      selectedFormat = "PDF";
    } else if (format === "caj" && cajLink) {
      selected = cajLink;
      selectedFormat = "CAJ";
    } else if (pdfLink) {
      selected = pdfLink;
      selectedFormat = "PDF";
    } else if (cajLink) {
      selected = cajLink;
      selectedFormat = "CAJ";
    }

    if (!selected) {
      return {
        error: "cnki_download_unavailable",
        message: "No direct PDF/CAJ download link found.",
        title,
        hasPDF: !!pdfLink,
        hasCAJ: !!cajLink,
        url: location.href,
        bodyHint: bodyText.slice(0, 500),
      };
    }

    selected.click();
    return {
      status: "cnki_download_triggered",
      format: selectedFormat,
      title,
      url: location.href,
      linkText: selected.innerText?.trim() || "",
      href: selected.href || "",
    };
  } catch (error) {
    return {
      error: "cnki_page_not_ready",
      message: String(error && error.message ? error.message : error),
      title: document.title,
      url: location.href,
      bodyHint: (document.body?.innerText || "").slice(0, 500),
    };
  }
};

module.exports = {
  cnkiBasicSearch,
  cnkiPaperDetail,
  cnkiDirectDownload,
};
