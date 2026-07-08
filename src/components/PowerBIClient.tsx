import { useEffect, useRef } from "react";

export default function PowerBIClient() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function loadPowerBI() {
      const powerbi = await import("powerbi-client");
      const { models } = powerbi;

      const response = await fetch("http://127.0.0.1:8000/api/powerbi/embed");
      const data = await response.json();

      const report = {
        type: "report",
        id: data.reportId,
        embedUrl: data.embedUrl,
        accessToken: data.accessToken,
        tokenType: models.TokenType.Embed,
        settings: {
          panes: {
            filters: { visible: false },
            pageNavigation: { visible: true },
          },
        },
      };

      const service = new powerbi.service.Service(
    powerbi.factories.hpmFactory,
    powerbi.factories.wpmpFactory,
    powerbi.factories.routerFactory
);

service.embed(containerRef.current!, report);
    }

    loadPowerBI();
  }, []);

  return (
    <div
      ref={containerRef}
      className="h-full w-full"
    />
  );
}