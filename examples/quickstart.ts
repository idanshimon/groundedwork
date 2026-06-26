/**
 * Quickstart — the 60-second tour of groundedwork (TypeScript).
 *
 * Run:  node --experimental-strip-types examples/quickstart.ts
 *       (from the ts/ dir, or adjust the import path)
 */
import { GroundedWork } from "../ts/src/index.ts";

const kb = new GroundedWork().addMany([
  { id: "returns", title: "Returns & Refunds", body: "Return any unopened bag within 30 days for a full refund. Opened bags get store credit." },
  { id: "shipping", title: "US Shipping", body: "Orders arrive in 3 to 5 business days. Free shipping on orders over $40." },
  { id: "decaf", title: "Decaf Options", body: "Every coffee is available decaffeinated using the Swiss Water process." },
]);

console.log("== a question the docs CAN answer ==");
console.log(kb.ask("How do I get a refund?"));
// { grounded: true, answer: "Return any unopened bag...", source: "returns" }

console.log("\n== a question the docs CANNOT answer ==");
console.log(kb.ask("What's the capital of France?"));
// { grounded: false, answer: "I don't have that...", source: null }

console.log("\n== cache-optimal payload for your own model call ==");
const m = kb.messages("How do I get a refund?");
console.log("grounded:", m.grounded, "| sources:", m.sources);
console.log("messages:", m.messages.map((x) => x.role).join(" -> "));
// grounded: true | sources: ["returns"]
// messages: system -> user -> user   (system=stable prefix, then knowledge, then question)
