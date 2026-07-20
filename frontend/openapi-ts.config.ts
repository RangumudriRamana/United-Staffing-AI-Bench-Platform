import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  client: "legacy/axios",
  input: "http://localhost:3000/openapi.json",
  output: "src/api/generated",
});
