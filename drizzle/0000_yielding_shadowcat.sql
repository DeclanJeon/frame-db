CREATE TABLE `categories` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`group_name` text NOT NULL,
	`description` text NOT NULL,
	`target` integer DEFAULT 1400 NOT NULL,
	`sort` integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE `collection_entries` (
	`collection_id` text NOT NULL,
	`entry_id` text NOT NULL,
	`note` text DEFAULT '' NOT NULL,
	`created` text NOT NULL,
	PRIMARY KEY(`collection_id`, `entry_id`),
	FOREIGN KEY (`collection_id`) REFERENCES `collections`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`entry_id`) REFERENCES `reference_entries`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `collections` (
	`id` text PRIMARY KEY NOT NULL,
	`owner_id` text NOT NULL,
	`name` text NOT NULL,
	`created` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `collection_owner_idx` ON `collections` (`owner_id`);--> statement-breakpoint
CREATE TABLE `reference_entries` (
	`id` text PRIMARY KEY NOT NULL,
	`category_id` text NOT NULL,
	`source_id` text NOT NULL,
	`title` text NOT NULL,
	`original_title` text DEFAULT '' NOT NULL,
	`description` text NOT NULL,
	`gender` text NOT NULL,
	`subtype` text NOT NULL,
	`status` text NOT NULL,
	`search_text` text NOT NULL,
	`details` text NOT NULL,
	`version` integer DEFAULT 1 NOT NULL,
	`updated` text NOT NULL,
	FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`source_id`) REFERENCES `sources`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE INDEX `entry_category_idx` ON `reference_entries` (`category_id`);--> statement-breakpoint
CREATE INDEX `entry_source_idx` ON `reference_entries` (`source_id`);--> statement-breakpoint
CREATE INDEX `entry_gender_idx` ON `reference_entries` (`gender`);--> statement-breakpoint
CREATE INDEX `entry_subtype_idx` ON `reference_entries` (`subtype`);--> statement-breakpoint
CREATE TABLE `entry_tags` (
	`entry_id` text NOT NULL,
	`tag_id` text NOT NULL,
	PRIMARY KEY(`entry_id`, `tag_id`),
	FOREIGN KEY (`entry_id`) REFERENCES `reference_entries`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`tag_id`) REFERENCES `tags`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE INDEX `tags_entry_idx` ON `entry_tags` (`tag_id`);--> statement-breakpoint
CREATE TABLE `import_batches` (
	`id` text PRIMARY KEY NOT NULL,
	`source_id` text NOT NULL,
	`expected` integer NOT NULL,
	`indexed` integer NOT NULL,
	`groups` integer NOT NULL,
	`status` text NOT NULL,
	`report` text NOT NULL,
	`checked` text NOT NULL,
	FOREIGN KEY (`source_id`) REFERENCES `sources`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `media_assets` (
	`id` text PRIMARY KEY NOT NULL,
	`entry_id` text NOT NULL,
	`variant_id` text,
	`kind` text NOT NULL,
	`url` text NOT NULL,
	`availability` text NOT NULL,
	`source_id` text NOT NULL,
	`original_id` text NOT NULL,
	FOREIGN KEY (`entry_id`) REFERENCES `reference_entries`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`variant_id`) REFERENCES `entry_variants`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`source_id`) REFERENCES `sources`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE INDEX `media_entry_idx` ON `media_assets` (`entry_id`);--> statement-breakpoint
CREATE TABLE `prompt_templates` (
	`id` text PRIMARY KEY NOT NULL,
	`entry_id` text NOT NULL,
	`text` text NOT NULL,
	`language` text NOT NULL,
	`authorship` text NOT NULL,
	`parameters` text NOT NULL,
	FOREIGN KEY (`entry_id`) REFERENCES `reference_entries`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE INDEX `prompt_entry_idx` ON `prompt_templates` (`entry_id`);--> statement-breakpoint
CREATE TABLE `entry_relations` (
	`id` text PRIMARY KEY NOT NULL,
	`from_id` text NOT NULL,
	`to_id` text NOT NULL,
	`type` text NOT NULL,
	`reason` text NOT NULL,
	FOREIGN KEY (`from_id`) REFERENCES `reference_entries`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`to_id`) REFERENCES `reference_entries`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE INDEX `relation_from_idx` ON `entry_relations` (`from_id`);--> statement-breakpoint
CREATE TABLE `seed_state` (
	`id` text PRIMARY KEY NOT NULL,
	`status` text NOT NULL,
	`updated` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `skill_mappings` (
	`id` text PRIMARY KEY NOT NULL,
	`category_id` text NOT NULL,
	`path` text NOT NULL,
	`slots` text NOT NULL,
	`version` text NOT NULL,
	FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `sources` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`url` text,
	`license` text NOT NULL,
	`hosting` text NOT NULL,
	`checked` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `tags` (
	`id` text PRIMARY KEY NOT NULL,
	`label` text NOT NULL,
	`kind` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `entry_variants` (
	`id` text PRIMARY KEY NOT NULL,
	`entry_id` text NOT NULL,
	`label` text NOT NULL,
	`angle` text,
	`attributes` text NOT NULL,
	FOREIGN KEY (`entry_id`) REFERENCES `reference_entries`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE INDEX `variant_entry_idx` ON `entry_variants` (`entry_id`);--> statement-breakpoint
CREATE TABLE `entry_versions` (
	`id` text PRIMARY KEY NOT NULL,
	`entry_id` text NOT NULL,
	`version` integer NOT NULL,
	`snapshot` text NOT NULL,
	`note` text NOT NULL,
	FOREIGN KEY (`entry_id`) REFERENCES `reference_entries`(`id`) ON UPDATE no action ON DELETE no action
);
