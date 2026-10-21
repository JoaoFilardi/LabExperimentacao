# Deployment rework rate vs CFR (b)

Heurística: `semver_patch` (título+corpo). Janela: 2025-10-01 a 2026-09-30. Rework rate agregado: 0.7374.

## Resumo

|  | n | média | mediana | Q1 | Q3 | mín | máx |
|---|---|---|---|---|---|---|---|
| rework_rate | 180 | 0.6564 | 0.7183 | 0.4939 | 0.8981 | 0.0000 | 1.0000 |
| cfr_b_recalculado | 180 | 0.3484 | 0.3333 | 0.0890 | 0.5690 | 0.0000 | 0.9841 |
| cfr_delivery_proxy | 310 | 0.3077 | 0.2935 | 0.2015 | 0.4057 | 0.0000 | 0.9562 |

## Por repositório

| full_name | total_releases | releases_corretivas | rework_rate | cfr_b_recalculado | cfr_delivery_proxy | contagem_confere | cfr_confere |
|---|---|---|---|---|---|---|---|
| mattpocock/skills | 7.0000 | 3.0000 | 0.4286 | 0.5714 | 0.5714 | True | True |
| react/react | 28.0000 | 25.0000 | 0.8929 | 0.6429 | 0.6429 | True | True |
| n8n-io/n8n | 257.0000 | 247.0000 | 0.9611 | 0.9841 | 0.9562 | True | False |
| yt-dlp/yt-dlp | 14.0000 | 14.0000 | 1.0000 | 0.2143 | 0.1429 | True | False |
| firecrawl/firecrawl | 8.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | True | True |
| tiangolo/fastapi | 92.0000 | 68.0000 | 0.7391 | 0.7416 | 0.2642 | False | False |
| pydantic/pydantic | 14.0000 | 12.0000 | 0.8571 | 0.5000 | 0.2932 | False | False |
| pallets/flask | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.2433 | False | False |
| django/django |  |  |  |  | 0.1058 | False | False |
| encode/httpx |  |  |  |  | 0.3789 | False | False |
| psf/requests | 5.0000 | 3.0000 | 0.6000 | 0.6000 | 0.1273 | True | False |
| scikit-learn/scikit-learn | 3.0000 | 1.0000 | 0.3333 | 0.0000 | 0.1210 | False | False |
| pytest-dev/pytest | 6.0000 | 4.0000 | 0.6667 | 0.3333 | 0.0989 | False | False |
| celery/celery | 4.0000 | 3.0000 | 0.7500 | 0.2500 | 0.1479 | False | False |
| sqlalchemy/sqlalchemy | 13.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2007 | False | False |
| vuejs/core | 20.0000 | 20.0000 | 1.0000 | 0.1000 | 0.2022 | False | False |
| angular/angular | 117.0000 | 105.0000 | 0.8974 | 0.7965 | 0.4413 | False | False |
| expressjs/express | 5.0000 | 3.0000 | 0.6000 | 0.6000 | 0.5934 | False | False |
| nestjs/nest | 38.0000 | 35.0000 | 0.9211 | 0.5405 | 0.1834 | False | False |
| vitejs/vite | 80.0000 | 64.0000 | 0.8000 | 0.7089 | 0.2187 | False | False |
| facebook/docusaurus | 4.0000 | 3.0000 | 0.7500 | 0.0000 | 0.5442 | False | False |
| tailwindlabs/tailwindcss | 16.0000 | 14.0000 | 0.8750 | 0.3125 | 0.2775 | False | False |
| reduxjs/redux |  |  |  |  | 0.5153 | False | False |
| apollographql/apollo-client | 36.0000 | 30.0000 | 0.8333 | 0.5833 | 0.6352 | False | False |
| tokio-rs/tokio | 17.0000 | 11.0000 | 0.6471 | 0.5882 | 0.3781 | False | False |
| serde-rs/serde | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.3688 | False | False |
| gin-gonic/gin | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2010 | False | False |
| spring-projects/spring-boot | 24.0000 | 22.0000 | 0.9167 | 0.5417 | 0.4690 | False | False |
| facebook/react-native | 28.0000 | 22.0000 | 0.7857 | 0.4643 | 0.2128 | False | False |
| grafana/grafana | 97.0000 | 93.0000 | 0.9588 | 0.7849 | 0.4683 | False | False |
| prometheus/prometheus | 25.0000 | 16.0000 | 0.6400 | 0.3333 | 0.2073 | False | False |
| mattermost/mattermost | 90.0000 | 81.0000 | 0.9000 | 0.7079 | 0.2255 | False | False |
| supabase/supabase | 8.0000 | 8.0000 | 1.0000 | 0.0000 | 0.2827 | False | False |
| home-assistant/core | 57.0000 | 45.0000 | 0.7895 | 0.5893 | 0.4595 | False | False |
| mastodon/mastodon | 64.0000 | 61.0000 | 0.9531 | 0.6719 | 0.5475 | False | False |
| directus/directus | 29.0000 | 19.0000 | 0.6552 | 0.4483 | 0.2135 | False | False |
| zulip/zulip | 8.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2592 | False | False |
| metabase/metabase | 144.0000 | 144.0000 | 1.0000 | 0.8333 | 0.1665 | False | False |
| strapi/strapi | 61.0000 | 28.0000 | 0.4590 | 0.3220 | 0.4750 | False | False |
| calcom/cal.com | 70.0000 | 64.0000 | 0.9143 | 0.9714 | 0.3730 | False | False |
| appwrite/appwrite | 10.0000 | 4.0000 | 0.4000 | 0.0000 | 0.2492 | False | False |
| discourse/discourse |  |  |  |  | 0.1403 | False | False |
| goharbor/harbor | 10.0000 | 9.0000 | 0.9000 | 0.4000 | 0.1927 | False | False |
| argoproj/argo-cd | 54.0000 | 51.0000 | 0.9444 | 0.6111 | 0.0826 | False | False |
| hashicorp/vault | 12.0000 | 9.0000 | 0.7500 | 0.0833 | 0.3928 | False | False |
| keycloak/keycloak | 25.0000 | 22.0000 | 0.8800 | 0.1250 | 0.4308 | False | False |
| BurntSushi/ripgrep | 3.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1759 | False | False |
| sharkdp/bat | 2.0000 | 1.0000 | 0.5000 | 0.0000 | 0.3261 | False | False |
| sharkdp/fd | 4.0000 | 2.0000 | 0.5000 | 0.5000 | 0.7185 | False | False |
| cli/cli | 28.0000 | 7.0000 | 0.2500 | 0.1852 | 0.4058 | False | False |
| helm/helm | 29.0000 | 22.0000 | 0.7586 | 0.4138 | 0.2524 | False | False |
| jesseduffield/lazygit | 17.0000 | 7.0000 | 0.4118 | 0.1176 | 0.3891 | False | False |
| charmbracelet/gum | 3.0000 | 2.0000 | 0.6667 | 0.0000 | 0.2096 | False | False |
| starship/starship | 6.0000 | 3.0000 | 0.5000 | 0.0000 | 0.1335 | False | False |
| denoland/deno | 44.0000 | 40.0000 | 0.9091 | 0.5682 | 0.2122 | False | False |
| oven-sh/bun | 18.0000 | 16.0000 | 0.8889 | 0.1111 | 0.3320 | False | False |
| astral-sh/uv | 101.0000 | 97.0000 | 0.9604 | 0.9082 | 0.4292 | False | False |
| astral-sh/ruff | 48.0000 | 45.0000 | 0.9375 | 0.3617 | 0.3640 | False | False |
| cloudflare/cloudflared | 25.0000 | 16.0000 | 0.6400 | 0.3043 | 0.6208 | False | False |
| psf/black | 7.0000 | 2.0000 | 0.2857 | 0.2857 | 0.2222 | False | False |
| pylint-dev/pylint | 14.0000 | 12.0000 | 0.8571 | 0.2727 | 0.3150 | True | False |
| tiangolo/sqlmodel | 22.0000 | 22.0000 | 1.0000 | 0.6364 | 0.1368 | False | False |
| encode/starlette | 22.0000 | 9.0000 | 0.4091 | 0.4091 | 0.5361 | False | False |
| encode/uvicorn | 23.0000 | 6.0000 | 0.2609 | 0.2273 | 0.2143 | False | False |
| aio-libs/aiohttp | 10.0000 | 8.0000 | 0.8000 | 0.3000 | 0.2151 | False | False |
| numpy/numpy | 13.0000 | 11.0000 | 0.8462 | 0.0769 | 0.4251 | False | False |
| pandas-dev/pandas | 7.0000 | 6.0000 | 0.8571 | 0.0000 | 0.4504 | False | False |
| scipy/scipy | 5.0000 | 3.0000 | 0.6000 | 0.0000 | 0.2184 | False | False |
| matplotlib/matplotlib | 6.0000 | 5.0000 | 0.8333 | 0.0000 | 0.2170 | False | False |
| seaborn/seaborn |  |  |  |  | 0.1578 | False | False |
| huggingface/transformers | 40.0000 | 21.0000 | 0.5250 | 0.4103 | 0.3902 | False | False |
| huggingface/datasets | 17.0000 | 9.0000 | 0.5294 | 0.3529 | 0.2960 | False | False |
| gradio-app/gradio | 945.0000 | 687.0000 | 0.7270 | 0.9520 | 0.4055 | False | False |
| vllm-project/vllm | 32.0000 | 12.0000 | 0.3750 | 0.2812 | 0.1560 | False | False |
| langchain-ai/langchain | 389.0000 | 276.0000 | 0.7095 | 0.9580 | 0.4058 | False | False |
| run-llama/llama_index | 20.0000 | 20.0000 | 1.0000 | 0.1500 | 0.1211 | False | False |
| tiangolo/typer | 26.0000 | 18.0000 | 0.6923 | 0.5385 | 0.4507 | False | False |
| textualize/rich | 7.0000 | 4.0000 | 0.5714 | 0.1429 | 0.3640 | False | False |
| textualize/textual | 35.0000 | 16.0000 | 0.4571 | 0.3429 | 0.4538 | False | False |
| pallets/click | 7.0000 | 5.0000 | 0.7143 | 0.1429 | 0.3698 | True | False |
| pallets/jinja |  |  |  |  | 0.5135 | False | False |
| sqlalchemy/alembic | 13.0000 | 0.0000 | 0.0000 | 0.0000 | 0.3943 | False | False |
| statsmodels/statsmodels | 2.0000 | 1.0000 | 0.5000 | 0.0000 | 0.2630 | False | False |
| sympy/sympy |  |  |  |  | 0.2003 | False | False |
| jupyter/notebook | 12.0000 | 10.0000 | 0.8333 | 0.0000 | 0.2600 | True | False |
| ipython/ipython |  |  |  |  | 0.2660 | False | False |
| bokeh/bokeh |  |  |  |  | 0.2214 | False | False |
| dask/dask | 15.0000 | 7.0000 | 0.4667 | 0.3333 | 0.3600 | True | False |
| ray-project/ray | 16.0000 | 7.0000 | 0.4375 | 0.2500 | 0.3466 | False | False |
| pyinstaller/pyinstaller | 9.0000 | 3.0000 | 0.3333 | 0.1111 | 0.2919 | False | False |
| pre-commit/pre-commit | 6.0000 | 3.0000 | 0.5000 | 0.0000 | 0.1489 | False | False |
| cookiecutter/cookiecutter | 2.0000 | 1.0000 | 0.5000 | 0.5000 | 0.4668 | False | False |
| certbot/certbot | 10.0000 | 3.0000 | 0.3000 | 0.2000 | 0.4351 | False | False |
| vercel/next.js | 78.0000 | 74.0000 | 0.9487 | 0.7600 | 0.5698 | False | False |
| facebook/jest | 7.0000 | 4.0000 | 0.5714 | 0.4286 | 0.6263 | False | False |
| remix-run/react-router | 33.0000 | 19.0000 | 0.5758 | 0.2424 | 0.5284 | False | False |
| sveltejs/svelte | 113.0000 | 95.0000 | 0.8407 | 0.8673 | 0.3102 | False | False |
| sveltejs/kit | 124.0000 | 86.0000 | 0.6935 | 0.8710 | 0.3446 | False | False |
| solidjs/solid |  |  |  |  | 0.3565 | False | False |
| preactjs/preact | 17.0000 | 14.0000 | 0.8235 | 0.3125 | 0.4743 | False | False |
| electron/electron | 184.0000 | 118.0000 | 0.6413 | 0.8539 | 0.0845 | False | False |
| gatsbyjs/gatsby | 2.0000 | 1.0000 | 0.5000 | 0.0000 | 0.5921 | False | False |
| nuxt/nuxt | 29.0000 | 23.0000 | 0.7931 | 0.4138 | 0.4040 | False | False |
| storybookjs/storybook | 85.0000 | 78.0000 | 0.9176 | 0.7976 | 0.3264 | False | False |
| prettier/prettier | 20.0000 | 17.0000 | 0.8500 | 0.6000 | 0.1549 | False | False |
| eslint/eslint | 27.0000 | 12.0000 | 0.4444 | 0.1852 | 0.4555 | False | False |
| babel/babel | 19.0000 | 17.0000 | 0.8947 | 0.3158 | 0.1147 | True | False |
| webpack/webpack | 29.0000 | 20.0000 | 0.6897 | 0.6207 | 0.2242 | False | False |
| rollup/rollup | 37.0000 | 26.0000 | 0.7027 | 0.3611 | 0.5277 | False | False |
| prisma/prisma | 23.0000 | 8.0000 | 0.3478 | 0.1739 | 0.2225 | False | False |
| typeorm/typeorm | 7.0000 | 5.0000 | 0.7143 | 0.1429 | 0.2460 | False | False |
| sequelize/sequelize | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.5150 | False | False |
| trpc/trpc | 20.0000 | 8.0000 | 0.4000 | 0.3000 | 0.1627 | False | False |
| fastify/fastify | 23.0000 | 17.0000 | 0.7391 | 0.4348 | 0.3455 | False | False |
| koajs/koa | 9.0000 | 7.0000 | 0.7778 | 0.4444 | 0.3556 | False | False |
| socketio/socket.io | 29.0000 | 28.0000 | 0.9655 | 0.6400 | 0.2355 | False | False |
| pmndrs/zustand | 7.0000 | 7.0000 | 1.0000 | 0.0000 | 0.1846 | False | False |
| tanstack/query | 811.0000 | 670.0000 | 0.8261 | 0.9737 | 0.3197 | False | False |
| chartjs/Chart.js | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.1320 | False | False |
| d3/d3 |  |  |  |  | 0.2027 | False | False |
| mrdoob/three.js | 6.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2698 | False | False |
| mermaid-js/mermaid | 49.0000 | 26.0000 | 0.5306 | 0.4694 | 0.3740 | False | False |
| ant-design/ant-design | 44.0000 | 35.0000 | 0.7955 | 0.3864 | 0.4683 | False | False |
| mui/material-ui | 18.0000 | 13.0000 | 0.7222 | 0.2222 | 0.1951 | False | False |
| shadcn-ui/ui | 65.0000 | 35.0000 | 0.5385 | 0.4769 | 0.4900 | False | False |
| puppeteer/puppeteer | 130.0000 | 55.0000 | 0.4231 | 0.6385 | 0.4694 | False | False |
| microsoft/playwright | 14.0000 | 6.0000 | 0.4286 | 0.2143 | 0.2201 | False | False |
| cypress-io/cypress | 30.0000 | 10.0000 | 0.3333 | 0.1379 | 0.2653 | False | False |
| pnpm/pnpm | 111.0000 | 57.0000 | 0.5135 | 0.6961 | 0.2636 | False | False |
| golang/go |  |  |  |  | 0.3595 | False | False |
| kubernetes/kubernetes | 42.0000 | 39.0000 | 0.9286 | 0.6667 | 0.4134 | False | False |
| moby/moby | 57.0000 | 36.0000 | 0.6316 | 0.4909 | 0.2360 | False | False |
| etcd-io/etcd | 32.0000 | 31.0000 | 0.9688 | 0.6250 | 0.2287 | False | False |
| containerd/containerd | 43.0000 | 37.0000 | 0.8605 | 0.6053 | 0.1355 | False | False |
| coredns/coredns | 11.0000 | 9.0000 | 0.8182 | 0.1818 | 0.5073 | True | False |
| traefik/traefik | 65.0000 | 63.0000 | 0.9692 | 0.6769 | 0.2380 | False | False |
| caddyserver/caddy | 4.0000 | 4.0000 | 1.0000 | 0.0000 | 0.5785 | False | False |
| labstack/echo | 19.0000 | 11.0000 | 0.5789 | 0.4118 | 0.4749 | False | False |
| gofiber/fiber | 12.0000 | 6.0000 | 0.5000 | 0.2500 | 0.2528 | False | False |
| gorm.io/gorm |  |  |  |  | 0.3670 | False | False |
| sqlc-dev/sqlc | 2.0000 | 1.0000 | 0.5000 | 0.5000 | 0.2931 | False | False |
| spf13/cobra | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.3575 | False | False |
| spf13/viper |  |  |  |  | 0.1273 | False | False |
| urfave/cli | 13.0000 | 4.0000 | 0.3077 | 0.0000 | 0.4093 | False | False |
| uber-go/zap | 2.0000 | 1.0000 | 0.5000 | 0.0000 | 0.4309 | False | False |
| stretchr/testify | 2.0000 | 1.0000 | 0.5000 | 0.5000 | 0.3872 | False | False |
| golangci/golangci-lint | 22.0000 | 13.0000 | 0.5909 | 0.5238 | 0.3322 | False | False |
| goreleaser/goreleaser | 23.0000 | 17.0000 | 0.7391 | 0.3043 | 0.5490 | False | False |
| syncthing/syncthing | 11.0000 | 10.0000 | 0.9091 | 0.0000 | 0.3196 | False | False |
| minio/minio | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0870 | False | False |
| tailscale/tailscale | 27.0000 | 27.0000 | 1.0000 | 0.4231 | 0.4372 | False | False |
| fatedier/frp | 9.0000 | 3.0000 | 0.3333 | 0.0000 | 0.3398 | False | False |
| go-gitea/gitea | 17.0000 | 13.0000 | 0.7647 | 0.1875 | 0.0500 | False | False |
| grafana/loki | 40.0000 | 35.0000 | 0.8750 | 0.5250 | 0.1899 | False | False |
| victoriametrics/victoriametrics | 87.0000 | 60.0000 | 0.6897 | 0.5595 | 0.4913 | False | False |
| cockroachdb/cockroach |  |  |  |  | 0.5624 | False | False |
| milvus-io/milvus | 41.0000 | 39.0000 | 0.9512 | 0.4250 | 0.1152 | False | False |
| rust-lang/rust | 14.0000 | 6.0000 | 0.4286 | 0.0000 | 0.4113 | False | False |
| rust-lang/cargo |  |  |  |  | 0.2945 | False | False |
| rust-lang/rust-analyzer | 52.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1091 | True | False |
| alacritty/alacritty | 3.0000 | 1.0000 | 0.3333 | 0.3333 | 0.0551 | False | False |
| wez/wezterm |  |  |  |  | 0.2848 | False | False |
| helix-editor/helix |  |  |  |  | 0.2847 | False | False |
| zed-industries/zed | 130.0000 | 118.0000 | 0.9077 | 0.8837 | 0.2719 | False | False |
| hyperium/hyper | 7.0000 | 3.0000 | 0.4286 | 0.2857 | 0.4165 | False | False |
| seanmonstar/reqwest | 11.0000 | 10.0000 | 0.9091 | 0.4545 | 0.2942 | False | False |
| actix/actix-web | 39.0000 | 27.0000 | 0.6923 | 0.6667 | 0.2632 | False | False |
| tokio-rs/axum | 9.0000 | 8.0000 | 0.8889 | 0.5556 | 0.0582 | False | False |
| launchbadge/sqlx |  |  |  |  | 0.2629 | False | False |
| clap-rs/clap | 18.0000 | 18.0000 | 1.0000 | 0.4444 | 0.1993 | False | False |
| dani-garcia/vaultwarden | 14.0000 | 11.0000 | 0.7857 | 0.2857 | 0.2065 | False | False |
| meilisearch/meilisearch | 61.0000 | 29.0000 | 0.4754 | 0.4407 | 0.3911 | False | False |
| qdrant/qdrant | 12.0000 | 8.0000 | 0.6667 | 0.0000 | 0.0500 | False | False |
| vectordotdev/vector | 9.0000 | 1.0000 | 0.1111 | 0.0000 | 0.2059 | False | False |
| tauri-apps/tauri | 213.0000 | 122.0000 | 0.5728 | 0.8266 | 0.4513 | False | False |
| ratatui/ratatui | 35.0000 | 14.0000 | 0.4000 | 0.3429 | 0.4322 | False | False |
| casey/just | 20.0000 | 5.0000 | 0.2500 | 0.2000 | 0.0676 | False | False |
| spring-projects/spring-framework | 18.0000 | 17.0000 | 0.9444 | 0.5000 | 0.1179 | False | False |
| quarkusio/quarkus | 87.0000 | 75.0000 | 0.8621 | 0.7108 | 0.3690 | False | False |
| apache/kafka |  |  |  |  | 0.6664 | False | False |
| apache/spark |  |  |  |  | 0.2921 | False | False |
| apache/flink |  |  |  |  | 0.5140 | False | False |
| google/guava | 4.0000 | 2.0000 | 0.5000 | 0.3333 | 0.2140 | False | False |
| square/okhttp |  |  |  |  | 0.2911 | False | False |
| square/retrofit |  |  |  |  | 0.3415 | False | False |
| FasterXML/jackson-databind |  |  |  |  | 0.4730 | False | False |
| mockito/mockito | 4.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1648 | False | False |
| junit-team/junit5 | 11.0000 | 10.0000 | 0.9091 | 0.2727 | 0.4509 | False | False |
| curl/curl | 6.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1706 | False | False |
| neovim/neovim | 9.0000 | 8.0000 | 0.8889 | 0.0000 | 0.3721 | False | False |
| protocolbuffers/protobuf | 17.0000 | 0.0000 | 0.0000 | 0.0000 | 0.3654 | False | False |
| grpc/grpc | 12.0000 | 5.0000 | 0.4167 | 0.1667 | 0.2559 | False | False |
| facebook/rocksdb | 11.0000 | 10.0000 | 0.9091 | 0.2727 | 0.3383 | False | False |
| facebook/zstd |  |  |  |  | 0.4138 | False | False |
| nlohmann/json |  |  |  |  | 0.0982 | False | False |
| fmtlib/fmt | 2.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0500 | False | False |
| godotengine/godot | 11.0000 | 9.0000 | 0.8182 | 0.0909 | 0.3424 | False | False |
| rails/rails | 18.0000 | 17.0000 | 0.9444 | 0.7500 | 0.1555 | False | False |
| jekyll/jekyll |  |  |  |  | 0.0874 | False | False |
| puma/puma | 7.0000 | 4.0000 | 0.5714 | 0.1429 | 0.5561 | False | False |
| laravel/framework | 101.0000 | 27.0000 | 0.2673 | 0.4040 | 0.3052 | False | False |
| symfony/symfony | 83.0000 | 76.0000 | 0.9157 | 0.7375 | 0.2938 | False | False |
| composer/composer | 20.0000 | 17.0000 | 0.8500 | 0.5500 | 0.3202 | False | False |
| dotnet/runtime | 34.0000 | 32.0000 | 0.9412 | 0.5882 | 0.3839 | False | False |
| dotnet/aspnetcore | 34.0000 | 33.0000 | 0.9706 | 0.6176 | 0.1733 | False | False |
| PowerShell/PowerShell | 23.0000 | 22.0000 | 0.9565 | 0.6087 | 0.2013 | False | False |
| dart-lang/sdk |  |  |  |  | 0.4954 | False | False |
| flutter/flutter |  |  |  |  | 0.0791 | False | False |
| apple/swift | 9.0000 | 7.0000 | 0.7778 | 0.1111 | 0.1903 | False | False |
| JetBrains/kotlin | 8.0000 | 6.0000 | 0.7500 | 0.0000 | 0.2062 | False | False |
| ziglang/zig |  |  |  |  | 0.3106 | False | False |
| microsoft/platform-service-1 |  |  |  |  | 0.2726 | False | False |
| apache/platform-service-2 |  |  |  |  | 0.1527 | False | False |
| uber/platform-service-3 |  |  |  |  | 0.5423 | False | False |
| netflix/platform-service-4 |  |  |  |  | 0.1141 | False | False |
| cloudflare/platform-service-5 |  |  |  |  | 0.2508 | False | False |
| aws/platform-service-6 |  |  |  |  | 0.2577 | False | False |
| hashicorp/platform-service-7 |  |  |  |  | 0.5686 | False | False |
| facebook/platform-service-8 |  |  |  |  | 0.2269 | False | False |
| twitter/platform-service-9 |  |  |  |  | 0.1706 | False | False |
| google/platform-service-10 |  |  |  |  | 0.1636 | False | False |
| microsoft/platform-service-11 |  |  |  |  | 0.1977 | False | False |
| apache/platform-service-12 |  |  |  |  | 0.1106 | False | False |
| uber/platform-service-13 |  |  |  |  | 0.2864 | False | False |
| netflix/platform-service-14 |  |  |  |  | 0.0819 | False | False |
| cloudflare/platform-service-15 |  |  |  |  | 0.0980 | False | False |
| aws/platform-service-16 |  |  |  |  | 0.0691 | False | False |
| hashicorp/platform-service-17 |  |  |  |  | 0.2944 | False | False |
| facebook/platform-service-18 |  |  |  |  | 0.2437 | False | False |
| twitter/platform-service-19 |  |  |  |  | 0.3695 | False | False |
| google/platform-service-20 |  |  |  |  | 0.1388 | False | False |
| microsoft/platform-service-21 |  |  |  |  | 0.2965 | False | False |
| apache/platform-service-22 |  |  |  |  | 0.3096 | False | False |
| uber/platform-service-23 |  |  |  |  | 0.2748 | False | False |
| netflix/platform-service-24 |  |  |  |  | 0.3070 | False | False |
| cloudflare/platform-service-25 |  |  |  |  | 0.1537 | False | False |
| aws/platform-service-26 |  |  |  |  | 0.1215 | False | False |
| hashicorp/platform-service-27 |  |  |  |  | 0.1535 | False | False |
| facebook/platform-service-28 |  |  |  |  | 0.1557 | False | False |
| twitter/platform-service-29 |  |  |  |  | 0.2354 | False | False |
| google/platform-service-30 |  |  |  |  | 0.5077 | False | False |
| microsoft/platform-service-31 |  |  |  |  | 0.1975 | False | False |
| apache/platform-service-32 |  |  |  |  | 0.5447 | False | False |
| uber/platform-service-33 |  |  |  |  | 0.0696 | False | False |
| netflix/platform-service-34 |  |  |  |  | 0.3210 | False | False |
| cloudflare/platform-service-35 |  |  |  |  | 0.4492 | False | False |
| aws/platform-service-36 |  |  |  |  | 0.2045 | False | False |
| hashicorp/platform-service-37 |  |  |  |  | 0.1248 | False | False |
| facebook/platform-service-38 |  |  |  |  | 0.3037 | False | False |
| twitter/platform-service-39 |  |  |  |  | 0.3029 | False | False |
| google/platform-service-40 |  |  |  |  | 0.3622 | False | False |
| microsoft/platform-service-41 |  |  |  |  | 0.2436 | False | False |
| apache/platform-service-42 |  |  |  |  | 0.6643 | False | False |
| uber/platform-service-43 |  |  |  |  | 0.4364 | False | False |
| netflix/platform-service-44 |  |  |  |  | 0.3110 | False | False |
| cloudflare/platform-service-45 |  |  |  |  | 0.4501 | False | False |
| aws/platform-service-46 |  |  |  |  | 0.3491 | False | False |
| hashicorp/platform-service-47 |  |  |  |  | 0.3909 | False | False |
| facebook/platform-service-48 |  |  |  |  | 0.3084 | False | False |
| twitter/platform-service-49 |  |  |  |  | 0.3135 | False | False |
| google/platform-service-50 |  |  |  |  | 0.2683 | False | False |
| microsoft/platform-service-51 |  |  |  |  | 0.4692 | False | False |
| apache/platform-service-52 |  |  |  |  | 0.3170 | False | False |
| uber/platform-service-53 |  |  |  |  | 0.4941 | False | False |
| netflix/platform-service-54 |  |  |  |  | 0.2512 | False | False |
| cloudflare/platform-service-55 |  |  |  |  | 0.5001 | False | False |
| aws/platform-service-56 |  |  |  |  | 0.1714 | False | False |
| hashicorp/platform-service-57 |  |  |  |  | 0.2185 | False | False |
| facebook/platform-service-58 |  |  |  |  | 0.2720 | False | False |
| twitter/platform-service-59 |  |  |  |  | 0.0601 | False | False |
| google/platform-service-60 |  |  |  |  | 0.4688 | False | False |
| microsoft/platform-service-61 |  |  |  |  | 0.3375 | False | False |
| apache/platform-service-62 |  |  |  |  | 0.5109 | False | False |
| uber/platform-service-63 |  |  |  |  | 0.5271 | False | False |
| netflix/platform-service-64 |  |  |  |  | 0.2162 | False | False |
| cloudflare/platform-service-65 |  |  |  |  | 0.2435 | False | False |
| aws/platform-service-66 |  |  |  |  | 0.2639 | False | False |
| hashicorp/platform-service-67 |  |  |  |  | 0.1260 | False | False |
| facebook/platform-service-68 |  |  |  |  | 0.2729 | False | False |
| twitter/platform-service-69 |  |  |  |  | 0.4161 | False | False |
| google/platform-service-70 |  |  |  |  | 0.3895 | False | False |
| microsoft/platform-service-71 |  |  |  |  | 0.2678 | False | False |
| apache/platform-service-72 |  |  |  |  | 0.2275 | False | False |
| uber/platform-service-73 |  |  |  |  | 0.3437 | False | False |
| netflix/platform-service-74 |  |  |  |  | 0.2657 | False | False |
| cloudflare/platform-service-75 |  |  |  |  | 0.0668 | False | False |
| aws/platform-service-76 |  |  |  |  | 0.1657 | False | False |
| hashicorp/platform-service-77 |  |  |  |  | 0.5857 | False | False |
| facebook/platform-service-78 |  |  |  |  | 0.3448 | False | False |
| twitter/platform-service-79 |  |  |  |  | 0.2249 | False | False |
| google/platform-service-80 |  |  |  |  | 0.3345 | False | False |
| microsoft/platform-service-81 |  |  |  |  | 0.2520 | False | False |
| apache/platform-service-82 |  |  |  |  | 0.3791 | False | False |
| uber/platform-service-83 |  |  |  |  | 0.3767 | False | False |
| netflix/platform-service-84 |  |  |  |  | 0.1853 | False | False |
| cloudflare/platform-service-85 |  |  |  |  | 0.5042 | False | False |
| aws/platform-service-86 |  |  |  |  | 0.3254 | False | False |
| hashicorp/platform-service-87 |  |  |  |  | 0.3814 | False | False |
| facebook/platform-service-88 |  |  |  |  | 0.3827 | False | False |
| twitter/platform-service-89 |  |  |  |  | 0.1990 | False | False |
| google/platform-service-90 |  |  |  |  | 0.2794 | False | False |
| microsoft/platform-service-91 |  |  |  |  | 0.4557 | False | False |
| apache/platform-service-92 |  |  |  |  | 0.0500 | False | False |
| uber/platform-service-93 |  |  |  |  | 0.1192 | False | False |
| netflix/platform-service-94 |  |  |  |  | 0.4815 | False | False |
| cloudflare/platform-service-95 |  |  |  |  | 0.2393 | False | False |
| aws/platform-service-96 |  |  |  |  | 0.3245 | False | False |
| hashicorp/platform-service-97 |  |  |  |  | 0.3339 | False | False |
| facebook/platform-service-98 |  |  |  |  | 0.3270 | False | False |
| twitter/platform-service-99 |  |  |  |  | 0.3707 | False | False |
