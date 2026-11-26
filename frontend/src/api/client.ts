/**
 * TypeScript client for the latam-valuation-engine FastAPI backend.
 *
 * Endpoints (per the OpenAPI exposed by the Python backend):
 *   GET  /api/v1/health
 *   POST /api/v1/valuation/wacc
 *   POST /api/v1/valuation/dcf
 *   GET  /api/v1/valuation/macro/{country}
 *
 * The base URL is read from VITE_API_BASE_URL when set, otherwise
 * defaults to http://localhost:8000 during development.
 */

export type Country = "CO" | "AR" | "MX" | "CL" | "BR" | "PE" | "US";

export interface HealthResponse {
  status: string;
  version: string;
  service: string;
}

/**
 * Request payload for POST /api/v1/valuation/wacc.
 *
 * NOTE: The current backend (src/api/schemas/__init__.py) only reads
 * `country`, `beta_unlevered`, and `debt_to_total_capital_pct` from this
 * payload — the remaining defaults are pulled server-side from
 * `DEFAULTS_2026`. We send only the fields the backend accepts to avoid
 * spurious 422s; richer inputs can be added when the backend schema grows.
 */
export interface WACCRequest {
  country: Country;
  beta_unlevered: number;
  debt_to_total_capital_pct: number;
}

export interface WACCResponse {
  country: Country;
  cost_of_equity_pct: number;
  cost_of_debt_after_tax_pct: number;
  wacc_pct: number;
  country_risk_premium_applied_pct: number;
  components: Record<string, number | string>;
}

export interface DCFRequest {
  country: Country;
  flujos_base: number[];
  inversion_inicial: number;
  beta_unlevered: number;
  debt_to_total_capital_pct: number;
  n_iterations: number;
  growth_revenue_pesimista: number;
  growth_revenue_probable: number;
  growth_revenue_optimista: number;
  growth_costs_pesimista: number;
  growth_costs_probable: number;
  growth_costs_optimista: number;
  seed?: number | null;
}

export interface DCFResponse {
  country: Country;
  flujos_base: number[];
  wacc_pct: number;
  cost_of_equity_pct: number;
  vpn_mean: number;
  vpn_std: number;
  vpn_p05: number;
  vpn_p50: number;
  vpn_p95: number;
  prob_vpn_positivo: number;
  prob_tir_supera_wacc: number;
  tir_proyecto_mean: number;
  tir_inversionista_mean: number;
  n_iterations: number;
}

export interface MacroResponse {
  country: Country;
  as_of: string;
  inflation_yoy_pct: number;
  inflation_expectations_1y_pct: number;
  inflation_expectations_2y_pct: number;
  reference_rate_pct: number;
  embi_spread_bps: number;
  country_risk_premium_pct: number;
  equity_risk_premium_pct: number;
  fx_rate_to_usd: number;
  fx_volatility_30d_pct: number;
  unemployment_pct: number;
  gdp_growth_yoy_pct: number;
  min_wage_local: number;
  tax_rate_corp_pct: number;
  debt_to_gdp_pct: number;
  source: string;
}

const BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8000";

const API_PREFIX = "/api/v1";

class ApiError extends Error {
  status: number;
  detail: unknown;
  constructor(message: string, status: number, detail: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const url = `${BASE_URL}${API_PREFIX}${path}`;
  const headers = {
    "Content-Type": "application/json",
    Accept: "application/json",
    ...(init?.headers ?? {}),
  };

  const response = await fetch(url, { ...init, headers });

  if (!response.ok) {
    let detail: unknown;
    try {
      detail = await response.json();
    } catch {
      detail = await response.text();
    }
    throw new ApiError(
      `API ${init?.method ?? "GET"} ${path} failed: ${response.status} ${response.statusText}`,
      response.status,
      detail,
    );
  }

  return (await response.json()) as T;
}

export const api = {
  baseUrl: BASE_URL,

  health(): Promise<HealthResponse> {
    return request<HealthResponse>("/health", { method: "GET" });
  },

  computeWacc(req: WACCRequest): Promise<WACCResponse> {
    return request<WACCResponse>("/valuation/wacc", {
      method: "POST",
      body: JSON.stringify(req),
    });
  },

  computeDcf(req: DCFRequest): Promise<DCFResponse> {
    return request<DCFResponse>("/valuation/dcf", {
      method: "POST",
      body: JSON.stringify(req),
    });
  },

  getMacro(country: Country): Promise<MacroResponse> {
    return request<MacroResponse>(`/valuation/macro/${country}`, {
      method: "GET",
    });
  },
};

export { ApiError };
