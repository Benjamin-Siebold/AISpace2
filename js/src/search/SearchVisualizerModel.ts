import * as widgets from "@jupyter-widgets/base";
import * as packageJSON from "../../package.json";
import * as Analytics from "../Analytics";
import { IEvent } from "../Events";
import {
  deserializeGraph,
  Graph,
  IGraphJSON,
  ISearchGraphEdge,
  ISearchGraphNode,
  serializeGraph
} from "../Graph";
const EXTENSION_SPEC_VERSION = (packageJSON as any).version;

/**
 * The model that receives messages and synced traitlets from the backend.
 * See the accompanying backend file: `aispace2/jupyter/search/search.py`
 */
export default class SearchViewerModel extends widgets.DOMWidgetModel {
  public static serializers = Object.assign(
    {
      graph: {
        serialize: serializeGraph,
        deserialize: deserializeGraph
      }
    },
    widgets.DOMWidgetModel.serializers
  );

  public defaults() {
    return {
      ...super.defaults(),
      _model_module: "aispace2",
      _model_module_version: EXTENSION_SPEC_VERSION,
      _model_name: "SearchViewerModel",
      _view_module: "aispace2",
      _view_module_version: EXTENSION_SPEC_VERSION,
      _view_name: "SearchViewer",
      show_edge_costs: true,
      show_node_heuristics: false,
      layout_method: "force",
      _layout_root_id: null,
      _previously_rendered: false
    };
  }

  public initialize(attrs: any, opts: any) {
    super.initialize(attrs, opts);

    Analytics.trackApplet("search");

    // Forward message to views
    this.listenTo(this, "msg:custom", (event: IEvent) => {
      // We don't register a listener for Python messages (which go to the model) in the view,
      // because each new view would attach a new listener.
      // Instead, we register it once here, and broadcast it to views.
      this.trigger("view:msg", event);
    });
  }

  /** True if this model has not been rendered in any cell yet.
   *
   * This is used to work around timing issues: when the model is initialized,
   * the views may not be created, so sending a re-render message (to trigger the initial state)
   * doesn't work. Neither does sending a message from Python, for the same reason.
   * Instead, check if a view has rendered this model yet. If not, render the initial state.
   */
  get previouslyRendered(): boolean {
    return this.get("_previously_rendered");
  }

  /** The line width of the edges in the graph. */
  get lineWidth(): number {
    return this.get("line_width");
  }

  get textSize(): number {
    return this.get("text_size");
  }

  get detailLevel(): number {
    return this.get("detail_level");
  }
  
  // The time delay between consecutive display calls
  get sleepTime(): number {
    return this.get("sleep_time");
  }

  /** The Graph representing the search problem. */
  get graph(): Graph<ISearchGraphNode, ISearchGraphEdge> {
    return this.get("graph");
  }

  set graph(val: Graph<ISearchGraphNode, ISearchGraphEdge>) {
    this.set("graph", val);
  }

  // True if we want the child node to not include the text of its parent
  get showFullDomain(): boolean {
    return this.get("show_full_domain");
  }

  /** True if the visualization should show edge costs. */
  get showEdgeCosts(): boolean {
    return this.get("show_edge_costs");
  }

  /** True if a node's heuristic value should be shown. */
  get showNodeHeuristics(): boolean {
    return this.get("show_node_heuristics");
  }

  /** Controls the layout engine used. */
  get layoutMethod(): "force" | "tree" {
    return this.get("layout_method");
  }

  /**
   * The ID of the node to be used as the root of the tree.
   * Only applicable when using tree layout. Set automatically to the problem's start node.
   */
  get layoutRootId(): string {
    return this.get("_layout_root_id");
  }
}
